
#define DEBUG 1
#if DEBUG
#define LOG(x,y) Serial.print(x); Serial.println(y);
#else
#define LOG(x,y)
#endif

// defines ahorran ROM... aunque nos sobra de eso XD -- Verificar que los const vayan a la rom!
const uint8_t ANALOG_PRECISION_CMD  = 0x01;
const uint8_t ADD_INPUT_PIN_CMD     = 0x02;
const uint8_t ADD_OUTPUT_PIN_CMD    = 0x03;
const uint8_t SET_PIN_MODE_CMD      = 0x04;
const uint8_t SET_REPORT_MODE_CMD   = 0x05;
const uint8_t ACTUATE_CMD           = 0xF0;
const uint8_t RESET_PINS            = 0xFE;

// Commands executor caller -- one vector position == one command
int (*executor[255])(const char*);

int not_implemented(const char* data)
{
  //nothing to do...
  return 1;
}

typedef enum ReportModes {average, bulk, rt};

/** ---------------------------------------------------------- **/
/** GLOBAL CONFIG **/

uint8_t REPORT_READ_COUNT = 0;
uint8_t REPORT_READ_DELAY = 0;
ReportModes REPORT_MODE = average;
uint8_t INPUT_PORTS[129]; // Port count in first position
uint8_t ANALOG_PINS_COUNT = 0;
uint8_t DIGITAL_PINS_COUNT = 0;

/** ---------------------------------------------------------- **/

const char* ACK = "\xFF\x00";

/**
   ANALOG_PRECISION: 0x01 0x01 [BITS]
*/
int set_analog_precision(const char* data)
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
   PIN_MODE: 0x04 0x02 [PIN] [MODE]
*/
int set_pin_mode(const char* data)
{
  pinMode(data[2], data[3]);
  LOG("Changed pin mode on pin ", uint8_t(data[2]));
  LOG("Mode set to ", uint8_t(data[3]));

  return 4; // Command of 4 bytes
}

/**
   REPORT_MODE: 0x05 0x03 [MODE] [READ_COUNT] [READ_DELAY]
*/
int set_report_mode(const char* data)
{
  REPORT_MODE = (ReportModes)(data[2]);
  REPORT_READ_COUNT = byte(data[3]);
  REPORT_READ_DELAY = byte(data[4]);
  LOG("Report mode changed on port ", byte(data[3]));

  return 5; // Command of 5 bytes
}

/**
   ANALOG_INPUT: 0x02 0x01 [PORT]
*/
int set_analog_input(const char* data)
{
  INPUT_PORTS[0] += 1;
  INPUT_PORTS[INPUT_PORTS[0]] = byte(data[2]);

  if ( INPUT_PORTS[INPUT_PORTS[0]] >= A0 )
  {
    ANALOG_PINS_COUNT++;
    LOG("New analog input: ", byte(data[2]));
  } else
  {
    DIGITAL_PINS_COUNT++;
    LOG("New digital input: ", byte(data[2]));
  }

  return 3; // Command of 3 bytes
}
/**
   RESET: 0xFF
*/
int reset(const char* data)
{
  for ( int i = 1; i <= byte(INPUT_PORTS[0]); i++)
  {
    pinMode(INPUT_PORTS[i], OUTPUT);
  }

  INPUT_PORTS[0] = 0;
  ANALOG_PINS_COUNT = 0;
  DIGITAL_PINS_COUNT = 0;

  LOG("System reset executed", "");

  return 1;
}

/**
   ANALOG_OUTPUT: 0x03 0x01 [PORT]
*/
int set_analog_output(const char* data)
{
  // No se si vale la pena guardar registro de pines de salida...

  return 3; // Command of 3 bytes
}

/**
   ACTUATE: 0xF0 [DATA_LEN] [PIN_A] [VALUE_PIN_A] ... [PIN_N] [VALUE_PIN_N]
*/
int actuate(const char* data)
{
  int offset = 0;
  int byte_count = byte(data[1]); // Un byte puede llegar a limitar la cantidad de salidas... creo

  uint8_t digital_input_buffer[DIGITAL_PINS_COUNT][REPORT_READ_COUNT / 8 + 2]; // 255 lectures of 1 bit for every digital pin -- 1 extra byte for the port address
  uint8_t analog_input_buffer[ANALOG_PINS_COUNT][(2 * REPORT_READ_COUNT) + 2]; // 255 lectures of 2 bytes for every analog pin -- 1 extra byte for the port address

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

  delayMicroseconds(REPORT_READ_DELAY); // FIXME: Usamos variable de 8 bits cuando la precisión de esta función llega a 16 bits.

  char response[130];
  response[0] = '\xF1';
  uint16_t len = 0;  // Inicia en 1 para evitar pisar el id de comando

  // Resets of digital buffers (required due the buffering strategy for digital pins)
  memset(digital_input_buffer, 0, DIGITAL_PINS_COUNT * (REPORT_READ_COUNT / 8 + 2));

  for (int i = 0; i < DIGITAL_PINS_COUNT; i++)
  {
    for (int j = 0; j < REPORT_READ_COUNT / 8 + 1; j++)
    {
      Serial.print(digital_input_buffer[i][j], HEX);
    }
    Serial.println("");
  }

  // Tracks count of digital and analog ports
  LOG("Number of lectures to report: ", REPORT_READ_COUNT);
  for (int lecture = 0; lecture <= REPORT_READ_COUNT; lecture++)
  {
    uint8_t current_digital = 0;
    uint8_t current_analog = 0;
    for (int i = 1; i <= byte(INPUT_PORTS[0]); i++)
    {
      //response[len + 1] = INPUT_PORTS[i];
      if ( INPUT_PORTS[i] >= A0 )
      {
        LOG("Reading analog port A", INPUT_PORTS[i] - A0);
        int data = analogRead(INPUT_PORTS[i] - A0);
        //response[len + 2] = byte((data & 0xFF00) >> 8); // Se guarda el msb en el buffer
        //response[len + 3] = byte(data & 0xFF);        // Se guarda el lsb en el buffer
        analog_input_buffer[current_analog][0] = INPUT_PORTS[i];
        analog_input_buffer[current_analog][lecture + 1] = byte((data & 0xFF00) >> 8);
        analog_input_buffer[current_analog][lecture + 2] = byte(data & 0xFF);

        current_analog++;

        //len += 3; // Cada lectura de un recurso analógico ocupa dos bytes. FIXME: se puede optimizar con bajas resoluciones
        LOG("=====================================", "");
        LOG("Analog pin read: ", INPUT_PORTS[i]);
        LOG("Analog read value: ", data);
      } else
      {
        int data = digitalRead(INPUT_PORTS[i]);
        //response[len + 2] = byte(data);
        digital_input_buffer[current_digital][0] = INPUT_PORTS[i];
        digital_input_buffer[current_digital][(lecture / 8) + 1] += (byte(data) & 0x01) << (lecture % 8); // Just keep first bit
        current_digital++;
        //len += 2;
        LOG("=====================================", "");
        LOG("Digital pin read: ", INPUT_PORTS[i]);
        LOG("Raw read: ", data);
        LOG("Lecture: ", lecture);
        LOG("Filtered read: ", (byte(data) & 0x01));
        LOG("Left padding: ", (lecture % 8));
        LOG("Added: ",  (byte(data) & 0x01) << (lecture % 8));
        LOG("Digital read value: ", digital_input_buffer[current_digital - 1][(lecture / 8) + 1]);
      }
    };
  }

  // Every analog output will be in the buffer as
  if (ANALOG_PINS_COUNT > 0)
  {
    len += ANALOG_PINS_COUNT + ( (REPORT_READ_COUNT + 1) * 2);
  }

  if (DIGITAL_PINS_COUNT > 0)
  {
    len +=  DIGITAL_PINS_COUNT + (((REPORT_READ_COUNT + 1) / 8 ) + 1);
  }

  LOG("Reporting actuate results ", len - 1);
  response[1] = len;
  SerialUSB.write(response, 2); // 2 bytes extras por el id de comando y la longitud y -1 por el padding

  //response[len + 1] = INPUT_PORTS[i];
  if ( ANALOG_PINS_COUNT > 0)
  {
    SerialUSB.write(analog_input_buffer[0], ANALOG_PINS_COUNT + ((REPORT_READ_COUNT + 1) * 2 * ANALOG_PINS_COUNT));
    //SerialUSB.write(INPUT_PORTS[i]);
    //SerialUSB.write(analog_input_buffer[INPUT_PORTS[i] - A0], (REPORT_READ_COUNT + 1) * 2);
    LOG("Reported an analog port with a read count len of: ", (REPORT_READ_COUNT + 1) * 2 + 1);
  }
  
  if ( DIGITAL_PINS_COUNT > 0) {
    SerialUSB.write(digital_input_buffer[0], DIGITAL_PINS_COUNT + (((REPORT_READ_COUNT + 1) / 8 ) + 1) * DIGITAL_PINS_COUNT );
    LOG("Reported an digital port with a read count len of: ",  DIGITAL_PINS_COUNT + (((REPORT_READ_COUNT + 1) / 8 ) + 1) * DIGITAL_PINS_COUNT );
  }

  return len + 2;
}

void setup() {
  SerialUSB.begin(115200);

#if DEBUG
  Serial.begin(115200);
#endif

  for (int i = 0; i < 255; i++)
  {
    executor[i] = &not_implemented;
  }

  INPUT_PORTS[0] = 0;

  /**  Commands Callbacks  **/
  executor[ANALOG_PRECISION_CMD]  = &set_analog_precision;
  executor[ADD_INPUT_PIN_CMD]     = &set_analog_input;
  executor[ADD_OUTPUT_PIN_CMD]    = &set_analog_output;
  executor[SET_PIN_MODE_CMD]      = &set_pin_mode;
  executor[SET_REPORT_MODE_CMD]   = &set_report_mode;
  executor[ACTUATE_CMD]           = &actuate;
  executor[RESET_PINS]            = &reset;

//  executor[SET_PIN_MODE_CMD]("\x04\x02\x3E\x00");
//  executor[ANALOG_PRECISION_CMD]("\x01\x01\x0C");
//  executor[SET_REPORT_MODE_CMD]("\x05\x03\x00\x09\x00");
//  executor[ADD_INPUT_PIN_CMD]("\x02\x01\x3E");
//  executor[SET_PIN_MODE_CMD]("\x04\x02\x3E\x00");
//  //  executor[ADD_INPUT_PIN_CMD]("\x02\x01\x3F");
//  //  executor[SET_PIN_MODE_CMD]("\x04\x02\x3F\x00");
//  executor[ADD_INPUT_PIN_CMD]("\x02\x01\x28");
//  executor[SET_PIN_MODE_CMD]("\x04\x02\x28\x00");
//  executor[ADD_INPUT_PIN_CMD]("\x02\x01\x29");
//  executor[SET_PIN_MODE_CMD]("\x04\x02\x29\x00");
//  executor[ADD_INPUT_PIN_CMD]("\x02\x01\x2A");
//  executor[SET_PIN_MODE_CMD]("\x04\x02\x2A\x00");

}

void loop() {
  //executor[ACTUATE_CMD]("\xF0\x01\x2B\x01");

  if (SerialUSB.available() > 0)
  {
    LOG("USB serial data available ", SerialUSB.available());
    char input[64]; // Esto se reserva en el stack, tal vez hacerlo global consume menos recursos...

    byte b_read = 0;
    byte b_pos = 0;

    while (SerialUSB.available() > 0)
    {
      b_read += SerialUSB.readBytes(input, SerialUSB.available());
    }

    // Loop to process all commands received in the buffer
    while (b_pos < b_read)
    {
      LOG("Executing command: ", int(input[b_pos]));
      b_pos += executor[input[b_pos]](&input[b_pos]); // Does the callback for the command
      LOG("b_pos ", b_pos);
    }
  }

  delay(4000);
}
