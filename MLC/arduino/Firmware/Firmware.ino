#define DEBUG 0
#include "GenericArduinoController.h"

GenericArduinoController controller(SerialUSB);

void setup() {
  SerialUSB.begin(115200);

#if DEBUG
  Serial.begin(115200);
#endif

}

void loop() {
  controller.handle_commands();

  /**
   * HERE the user can insert any command
   */

}
