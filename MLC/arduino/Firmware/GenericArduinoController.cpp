#include "Arduino.h"
#include "GenericArduinoController.h"

#define DEBUG 1

#if DEBUG
#include <string.h>
#define __FILENAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)
#define LOG(x,y) Serial.print(__FILENAME__); Serial.print(":"); Serial.print(__LINE__);\
Serial.print(" -- [DEBUG] -- ");Serial.print(x); Serial.println(y);
#else
#define LOG(x,y)

void inline dump_digital_buffer(const int &digital_pins_count, const int &report_read_count, const uint8_t** digital_input_buffer)
{
    for (int i = 0; i < digital_pins_count; i++)
  {
    for (int j = 0; j < report_read_count / 8 + 1; j++)
    {
      Serial.print(digital_input_buffer[i][j], HEX);
    }
    Serial.println("");
  }
}

#endif
 
#define VERSION "0.1"

const char* ACK = "\xFF\x00";

GenericArduinoController::GenericArduinoController(Stream &stream): stream_(stream)
{

  for (int i = 0; i <= 255; i++)
  {
    executor[i] = &GenericArduinoController::not_implemented;
  }
  
  REPORT_READ_COUNT = 0;
  REPORT_READ_DELAY = 0;
  REPORT_MODE = average;
  INPUT_PORTS[0] = 0;
  ANALOG_PINS_COUNT = 0;
  DIGITAL_PINS_COUNT = 0;

  executor[ANALOG_PRECISION_CMD]  = &GenericArduinoController::set_analog_precision;
  executor[ADD_INPUT_PIN_CMD]     = &GenericArduinoController::set_analog_input;
  executor[ADD_OUTPUT_PIN_CMD]    = &GenericArduinoController::set_analog_output;
  executor[SET_PIN_MODE_CMD]      = &GenericArduinoController::set_pin_mode;
  executor[SET_REPORT_MODE_CMD]   = &GenericArduinoController::set_report_mode;
  executor[ACTUATE_CMD]           = &GenericArduinoController::actuate;
  executor[RESET_PINS]            = &GenericArduinoController::reset;
  executor[VERSION_RESPONSE]      = &GenericArduinoController::protocol_version;
}

void GenericArduinoController::handle_commands()
{
  if (stream_.available() > 0)
  {
    LOG("Data available ", stream_.available());
    char input[64]; // Esto se reserva en el stack, tal vez hacerlo global consume menos recursos...

    byte b_read = 0;
    byte b_pos = 0;

    while (stream_.available() > 0)
    {
      b_read += stream_.readBytes(input, stream_.available());
    }

    LOG("Bytes obtained: ", b_read);
    // Loop to process all commands received in the buffer
    while (b_pos < b_read)
    {
      LOG("command: ", int(input[b_pos]));
      b_pos += executor[input[b_pos]](this, &input[b_pos]); // Does the callback for the command
      LOG("b_pos ", b_pos);
    }
  }
  
   LOG("No data", "");
   
   delay(1000);
}

void GenericArduinoController::add_handler(uint8_t handler_id, int (*handler)(GenericArduinoController* this_, const char*))
{
    executor[VERSION_RESPONSE] = handler;
}

// NULL operation
int GenericArduinoController::not_implemented(GenericArduinoController* this_, const char* data)
{
   return 1; //Breaks the loop
}

/**
 * PROTOCOL_VERSION 0x07 0x03 X . Y
 */
int GenericArduinoController::protocol_version(GenericArduinoController* this_, const char* data)
{
  char response[] = { char(VERSION_RESPONSE), char(0x03)};
  this_->stream_.write(response, 2);
  this_->stream_.write(VERSION, 3);
  return 1;
}

/**
 * ANALOG_WRITE: 0x06 0x03 [PIN] [H_VALUE][L_VALUE]
 */
int GenericArduinoController::analog_write(GenericArduinoController* this_, const char* data)
{
  uint16_t value = (data[3] << 8) + data[4];
  analogWrite(data[2], value);
  return 5;
}

/**
 *   ANALOG_PRECISION: 0x01 0x01 [BITS]
 */
int GenericArduinoController::set_analog_precision(GenericArduinoController* this_, const char* data)
{
  int i = byte(data[2]);
  // Tal vez conviene separar estas funciones ya que hay boards con resoluciones distintas...
  // Igual, así funciona bien con el due (y con todos, ya que no hay problema en superar el máximo de la resolución)
  analogWriteResolution(i);
  analogReadResolution(i);

  LOG("Resolution changed to: ", i);

  return 3; // Command of 3 bytes
}


/**
*   PIN_MODE: 0x04 0x02 [PIN] [MODE]
*/
int GenericArduinoController::set_pin_mode(GenericArduinoController* this_, const char* data)
{
  pinMode(data[2], data[3]);
  LOG("Changed pin mode on pin ", uint8_t(data[2]));
  LOG("Mode set to ", uint8_t(data[3]));

  return 4; // Command of 4 bytes
}

/**
*   REPORT_MODE: 0x05 0x03 [MODE] [READ_COUNT] [READ_DELAY]
*/
int GenericArduinoController::set_report_mode(GenericArduinoController* this_, const char* data)
{
  this_->REPORT_MODE = (ReportModes)(data[2]);
  this_->REPORT_READ_COUNT = byte(data[3]);
  this_->REPORT_READ_DELAY = byte(data[4]);
  LOG("Report mode changed", "")
  LOG("Report mode: ", this_->REPORT_MODE);
  LOG("New Read count: ", byte(data[3]));
  LOG("New Read delay: ", byte(data[4]));

  return 5; // Command of 5 bytes
}

/**
*   ANALOG_INPUT: 0x02 0x01 [PORT]
*/
int GenericArduinoController::set_analog_input(GenericArduinoController* this_, const char* data)
{
  this_->INPUT_PORTS[0] += 1;
  this_->INPUT_PORTS[this_->INPUT_PORTS[0]] = byte(data[2]);

  if ( this_->INPUT_PORTS[this_->INPUT_PORTS[0]] >= A0 )
  {
    this_->ANALOG_PINS_COUNT++;
    LOG("New analog input: ", byte(data[2]));
  } else
  {
    this_->DIGITAL_PINS_COUNT++;
    LOG("New digital input: ", byte(data[2]));
  }

  return 3; // Command of 3 bytes
}

/**
*   RESET: 0xFF
*/
int GenericArduinoController::reset(GenericArduinoController* this_, const char* data)
{
  for ( int i = 1; i <= byte(this_->INPUT_PORTS[0]); i++)
  {
    pinMode(this_->INPUT_PORTS[i], OUTPUT);
  }

  this_->INPUT_PORTS[0] = 0;
  this_->ANALOG_PINS_COUNT = 0;
  this_->REPORT_READ_COUNT = 0;
  this_->DIGITAL_PINS_COUNT = 0;

  LOG("System reset executed", "");

  return 1;
}

/**
*   ANALOG_OUTPUT: 0x03 0x01 [PORT]
*/
int GenericArduinoController::set_analog_output(GenericArduinoController* this_, const char* data)
{
  // No se si vale la pena guardar registro de pines de salida...

  return 3; // Command of 3 bytes
}

/**
*   ACTUATE: 0xF0 [DATA_LEN] [PIN_A] [VALUE_PIN_A] ... [PIN_N] [VALUE_PIN_N]
*/
int GenericArduinoController::actuate(GenericArduinoController* this_, const char* data)
{
  int offset = 0;
  int byte_count = byte(data[1]); // Un byte puede llegar a limitar la cantidad de salidas... creo

  uint8_t digital_input_buffer[this_->DIGITAL_PINS_COUNT][this_->REPORT_READ_COUNT / 8 + 2]; // 255 lectures of 1 bit for every digital pin -- 1 extra byte for the port address
  uint8_t analog_input_buffer[this_->ANALOG_PINS_COUNT][(2 * this_->REPORT_READ_COUNT) + 3]; // 255 lectures of 2 bytes for every analog pin -- 1 extra byte for the port address

  LOG("Actutating over payload of size: ", byte_count);

  // ACTUATION ZONE
  while (offset < byte_count)
  {
    //Se aplica la acción a cada puerto indicado
    int port = byte(data[2 + offset]);

    //Detects an analog port
    if ( port >= A0 )
    {
      int value = (data[3 + offset] << 8) + data[4 + offset];
      analogWrite(port, value);
      offset += 3;

      LOG("Analog pin written", port);
    } else
    {
      int value = data[3 + offset] > 0 ? HIGH : LOW; // Creo que da igual si pongo el entero directamente
      digitalWrite(port, value);
      offset += 2;

      LOG("Digital pin written ", port);
    }
  }

  delayMicroseconds(this_->REPORT_READ_DELAY); // FIXME: Usamos variable de 8 bits cuando la precisión de esta función llega a 16 bits.

  char response[130];
  response[0] = '\xF1';
  uint16_t len = 0;  // Inicia en 1 para evitar pisar el id de comando

  // Resets of digital buffers (required due the buffering strategy for digital pins)
  memset(digital_input_buffer, 0, this_->DIGITAL_PINS_COUNT * (this_->REPORT_READ_COUNT / 8 + 2));

  // Tracks count of digital and analog ports
  LOG("Number of lectures to report: ", this_->REPORT_READ_COUNT);
  for (int lecture = 0; lecture <= this_->REPORT_READ_COUNT; lecture++)
  {
    uint8_t current_digital = 0;
    uint8_t current_analog = 0;
    LOG("Input ports count: ", this_->INPUT_PORTS[0]);
    for (int i = 1; i <= byte(this_->INPUT_PORTS[0]); i++)
    {
      //response[len + 1] = INPUT_PORTS[i];
      if ( this_->INPUT_PORTS[i] >= A0 )
      {
        LOG("Reading analog port A", this_->INPUT_PORTS[i] - A0);
        int data = analogRead(this_->INPUT_PORTS[i] - A0);
        //response[len + 2] = byte((data & 0xFF00) >> 8); // Se guarda el msb en el buffer
        //response[len + 3] = byte(data & 0xFF);        // Se guarda el lsb en el buffer
        analog_input_buffer[current_analog][0] = this_->INPUT_PORTS[i];
        analog_input_buffer[current_analog][(lecture * 2) + 1] = byte((data & 0xFF00) >> 8);
        analog_input_buffer[current_analog][(lecture * 2) + 2] = byte(data & 0xFF);

        //len += 3; // Cada lectura de un recurso analógico ocupa dos bytes. FIXME: se puede optimizar con bajas resoluciones
        LOG("=====================================", "");
        LOG("Analog pin read: ", this_->INPUT_PORTS[i]);
        LOG("Analog read value: ", data);

        current_analog++;
      } else
      {
        int data = digitalRead(this_->INPUT_PORTS[i]);
        //response[len + 2] = byte(data);
        digital_input_buffer[current_digital][0] = this_->INPUT_PORTS[i];
        digital_input_buffer[current_digital][(lecture / 8) + 1] += (byte(data) & 0x01) << (lecture % 8); // Just keep first bit
        current_digital++;
        //len += 2;
        LOG("=====================================", "");
        LOG("Digital pin read: ", this_->INPUT_PORTS[i]);
        LOG("Raw read: ", data);
        LOG("Lecture: ", lecture);
        LOG("Filtered read: ", (byte(data) & 0x01));
        LOG("Left padding: ", (lecture % 8));
        LOG("Added: ",  (byte(data) & 0x01) << (lecture % 8));
        LOG("Digital read value: ", digital_input_buffer[current_digital - 1][(lecture / 8) + 1]);
      }
    };
  }

  LOG("Finish", "");

  // Every analog output will be in the buffer as
  if (this_->ANALOG_PINS_COUNT > 0)
  {
    len += this_->ANALOG_PINS_COUNT + ((this_->REPORT_READ_COUNT + 1) * 2 * this_->ANALOG_PINS_COUNT);
  }

  if (this_->DIGITAL_PINS_COUNT > 0)
  {
    len +=  this_->DIGITAL_PINS_COUNT + (((this_->REPORT_READ_COUNT + 1) / 8 ) + 1) * this_->DIGITAL_PINS_COUNT;
  }

  LOG("Reporting actuate results ", len - 1);
  LOG("No idea...", "");
  response[1] = len;
  this_->stream_.write(response, 2); // 2 bytes extras por el id de comando y la longitud y -1 por el padding

  //response[len + 1] = INPUT_PORTS[i];
  if ( this_->ANALOG_PINS_COUNT > 0)
  {
    this_->stream_.write(analog_input_buffer[0], this_->ANALOG_PINS_COUNT + ((this_->REPORT_READ_COUNT + 1) * 2 * this_->ANALOG_PINS_COUNT));
    //SerialUSB.write(INPUT_PORTS[i]);
    //SerialUSB.write(analog_input_buffer[INPUT_PORTS[i] - A0], (REPORT_READ_COUNT + 1) * 2);
    LOG("Reported an analog port with a read count len of: ", this_->ANALOG_PINS_COUNT + (this_->REPORT_READ_COUNT + 1) * 2 * this_->ANALOG_PINS_COUNT);
  }
  
  if ( this_->DIGITAL_PINS_COUNT > 0) {
    this_->stream_.write(digital_input_buffer[0], this_->DIGITAL_PINS_COUNT + (((this_->REPORT_READ_COUNT + 1) / 8 ) + 1) * this_->DIGITAL_PINS_COUNT );
    LOG("Reported an digital port with a read count len of: ",  this_->DIGITAL_PINS_COUNT + (((this_->REPORT_READ_COUNT + 1) / 8 ) + 1) * this_->DIGITAL_PINS_COUNT );
  }

  return len + 2;
}



