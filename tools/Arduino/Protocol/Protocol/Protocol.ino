#include "commands.h"
#include "CommandProcessor.h"

// Global variables
int G_ERROR_LED = 13;
CommandProcessor gCmdProcessor;

void setup() {
  // By the default, configure the serial port at this baudrate
  // Update the value of it with a command
  Serial.begin(115200);

  // Define the function ptr array
  setCmdFuncPtr();
  
  // We will use LED 13 to show that an error ocurred
  pinMode(G_ERROR_LED, OUTPUT);
}

void loop() {
  gCmdProcessor.readCommand();
}
