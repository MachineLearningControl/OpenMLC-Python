#include "GenericArduinoController.h"

#define DEBUG 1

GenericArduinoController controller(SerialUSB);

void setup() {
  SerialUSB.begin(115200);

#if DEBUG
  Serial.begin(115200);
#endif

}

void loop() {
  controller.handle_commands();

  Serial.println("Waiting for commands...");

  if (SerialUSB.available() > 0)
     Serial.println("Hay datos para leer...");

  /**
   * HERE the user can insert any command
   */

   delay(1000);
}
