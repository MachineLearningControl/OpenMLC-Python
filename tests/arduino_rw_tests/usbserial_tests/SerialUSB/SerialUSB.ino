#define BUF_N 1000

char buf[BUF_N];

const static int ANALOG_CHANNEL_COUNT = 11; //Cantidad de canales que se quieren publicar
const static short ADC_STRING_BUFFER = 6; //Tamanio del buffer de string de lecturas analógicas (12 bits de lecturas ==> 0 ~ 4095)

char* tostring(unsigned long input, char* output, unsigned len)
{
  static const unsigned BASE = 10; // Se puede volver a poner como parametro
  //char buf[8 * sizeof(long) + 1]; // Assumes 8-bit chars plus zero byte.

  char* number = output + len;

  size_t written = 0;
  *--number = '\0';

  do {
    char c = input % BASE;
    input /= BASE;

    *--number = c + '0';

    if (number == output && input != 0)
      return NULL;

  } while (input);


  return number;
}


void setup() {
  Serial.begin(115200);
  SerialUSB.begin(115200); // baud rate ignored for usb virtual serial
  memset(buf, 'A', BUF_N - 1);
  buf[BUF_N - 1] = '\0';
}

void loop() {
  //Serial.print(buf);
  if (SerialUSB.available() > 0)
  {
    char response[1000] = "    { \"Readings\":[";
    char input[64]; // 64 == Max Serial read buffer size
    while(SerialUSB.available()>0)
    {
//      Serial.println("Llego algo!");
      int read = SerialUSB.readBytes(input, SerialUSB.available());
//      Serial.print("Recibido: ");
//      Serial.write(input, read);
//      Serial.println("");
    }

    bool is_first = true;
    unsigned offset = 14;
    for (int analogChannel = 0; analogChannel < ANALOG_CHANNEL_COUNT; analogChannel++) {
      int sensorReading = analogRead(analogChannel);
      if (!is_first)
      {
        response[offset] = ',';
        response[offset + 1] = ' ';
        offset += 2;
      } else {
        is_first = false;
      }

      char buff[6];
      char* reading = tostring(sensorReading, buff, ADC_STRING_BUFFER);
      memcpy(response + offset, reading, ADC_STRING_BUFFER - (reading - buff));
      offset += 5 - (reading - buff);
    }
    response[offset] = ']';
    response[offset+1] = '}';
    offset += 2;

//      Serial.print("Respondiendo: ");
//      Serial.write(response, offset+1);
//      Serial.println("");
//  
    memcpy(response, reinterpret_cast<char*>(&offset), 4);
    //SerialUSB.write(reinterpret_cast<char*>(&offset), 4); // First bytes are the data count
    int write = SerialUSB.write(response, offset+4);
//    Serial.println(write);
  }
}
