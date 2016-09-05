/*
  Web Server

  A simple web server that shows the value of the analog input pins.
  using an Arduino Wiznet Ethernet shield.

  Circuit:
   Ethernet shield attached to pins 10, 11, 12, 13
   Analog inputs attached to pins A0 through A6 (Configurable por constante)

*/

#include <SPI.h>
#include <Ethernet.h>

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(192, 168, 1, 177);

const static int ANALOG_CHANNEL_COUNT = 11; //Cantidad de canales que se quieren publicar
const static short ADC_STRING_BUFFER = 6; //Tamanio del buffer de string de lecturas analógicas (12 bits de lecturas ==> 0 ~ 4095)

/**
  Retorna la representación en string de un entero sin signo

*/
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

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

void setup() {
  // start the Ethernet connection and the server:
  Ethernet.begin(mac, ip);
  Udp.begin(5000);
}

char packetBuffer[UDP_TX_PACKET_MAX_SIZE];  //buffer to hold incoming packet,

EthernetClient client;
void loop() {
  // listen for incoming clients

  char response[1000] = "[";
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
      Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
      //Serial.write(c);
      // if you've gotten to the end of the line (received a newline
      // character) and the line is blank, the http request has ended,
      // so you can send a reply
      // output the value of each analog input pin
      bool is_first = true;
      unsigned offset = 84;
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
      response[offset + 1] = '}';

      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write(response, offset+1);
      Udp.endPacket();

    delay(1);
  }
}
