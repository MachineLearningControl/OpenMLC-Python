
#define DEBUG 1

#ifdef DEBUG
#define LOG(x,y) Serial.print(x); Serial.println(y);
#endif

// defines ahorran ROM... aunque nos sobra de eso XD -- Verificar que los const vayan a la rom!
const uint8_t ANALOG_PRECISION_CMD  = 0x01;
const uint8_t ADD_INPUT_PORT_CMD  = 0x02;
const uint8_t ADD_OUTPUT_PORT_CMD = 0x03;
const uint8_t SET_PIN_MODE_CMD      = 0x04;
const uint8_t SET_REPORT_MODE_CMD   = 0x05;
const uint8_t ACTUATE_CMD           = 0xF0;

// Commands executor caller -- one vector position == one command
int (*executor[255])(const char*);

int not_implemented(const char* data)
{
  //nothing to do...
  return 0;
}

typedef enum ReportModes {average, bulk, rt};

/** ---------------------------------------------------------- **/
/** GLOBAL CONFIG **/

uint8_t REPORT_READ_COUNT = 0;
uint8_t REPORT_READ_DELAY = 0;
ReportModes REPORT_MODE = average;
uint8_t INPUT_PORTS[129]; // Port count in first position

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
  LOG("New analog input: ", byte(data[2]));

  return 3; // Command of 3 bytes
}

/**
 * ANALOG_OUTPUT: 0x03 0x01 [PORT]
 */
int set_analog_output(const char* data)
{
  // No se si vale la pena guardar registro de pines de salida...

  return 3; // Command of 3 bytes
}

/**
 * ACTUATE: 0xF0 [DATA_LEN] [PIN_A] [VALUE_PIN_A] ... [PIN_N] [VALUE_PIN_N]
 */
int actuate(const char* data)
{
  int offset = 0;
  int byte_count = byte(data[1]); // Un byte puede llegar a limitar la cantidad de salidas... creo

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
  byte len = 1;  // Inicia en 1 para evitar pisar el id de comando
  for (int i = 1; i <= byte(INPUT_PORTS[0]); i++)
  {
    if ( INPUT_PORTS[i] >= A0 )
    {
      int data = analogRead(INPUT_PORTS[i]-A0);
      response[len + 1] = byte((data & 0xFF00) >> 8); // Se guarda el msb en el buffer
      response[len + 2] = byte(data & 0xFF);        // Se guarda el lsb en el buffer

      len += 2; // Cada lectura de un recurso analógico ocupa dos bytes. FIXME: se puede optimizar con bajas resoluciones
      LOG("Analog pin read: ", INPUT_PORTS[i]);
    } else
    {
      int data = digitalRead(INPUT_PORTS[i]);
      response[len + 1] = byte(data);

      len += 1;
      LOG("Digital pin read: ", INPUT_PORTS[i]);
    }
  }

  response[1] = len - 1;
  SerialUSB.write(response, len + 2); // 2 bytes extras por el id de comando y la longitud

  return offset + 2;
}

void setup() {
  SerialUSB.begin(115200);
  
  #ifdef DEBUG
  Serial.begin(115200);
  #endif
  
  for (int i = 0; i < 255; i++)
  {
    executor[i] = &not_implemented;
  }

  INPUT_PORTS[0] = 0;

  /**  Commands Callbacks  **/
  executor[ANALOG_PRECISION_CMD]  = &set_analog_precision;
  executor[ADD_INPUT_PORT_CMD]  = &set_analog_input;
  executor[ADD_OUTPUT_PORT_CMD] = &set_analog_output;
  executor[SET_PIN_MODE_CMD]      = &set_pin_mode;
  executor[SET_REPORT_MODE_CMD]   = &set_report_mode;
  executor[ACTUATE_CMD]           = &actuate;

}

void loop() {
  //executor[ACTUATE_CMD]("\xF0\x01\x28\x01");

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
    while(b_pos < b_read)
    {
      LOG("Executing command: ", int(input[b_pos]));
      b_pos += executor[input[b_pos]](&input[b_pos]); // Does the callback for the command
      LOG("b_pos ", b_pos);
    }
  }
}
