#ifndef COMMANDS_H_
#define COMMANDS_H_

#include <stdint.h>

struct Command {
  uint8_t opcode;
  uint8_t size;
  uint8_t payload[64];
};

typedef void (*CmdFuncPtr)(Command* cmd);
extern int G_ERROR_LED;

// Function Declarations
void setCmdFuncPtr();
void initConfigCommand(Command* cmd);

// Initialize by default all the 
CmdFuncPtr gCmdFuncPtr[255] = {};

void setCmdFuncPtr() {
  gCmdFuncPtr[0] = initConfigCommand;
}

void initConfigCommand(Command* cmd) {
  // TODO:
  digitalWrite(G_ERROR_LED, HIGH);
}

#endif // COMMANDS_H_

