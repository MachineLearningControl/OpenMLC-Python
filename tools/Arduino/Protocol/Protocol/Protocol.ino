#include "CommandProcessor.h"
#include "commands.h"
#include "errors.h"
#include "util.h"

// Global variables
int G_ERROR_LED = 9;
CommandProcessor gCmdProcessor;
Command* cmd = NULL;

void setup() {
  // By the default, configure the serial port at this baudrate
  // Update the value of it with a command
  Serial.begin(9600);

  // Define the function ptr array
  setCmdFuncPtr();
  
  // We will use LED 13 to show that an error ocurred
  pinMode(G_ERROR_LED, OUTPUT);
}

void loop() {
  uint8_t error_code = NO_ERROR;
  cmd = gCmdProcessor.readCommand();
  if (cmd != NULL) {
    if (error_code = gCmdProcessor.processCommand(cmd)) {
      // Error ocurred
      blinkVariable(G_ERROR_LED, error_code);
    }
  }
}
