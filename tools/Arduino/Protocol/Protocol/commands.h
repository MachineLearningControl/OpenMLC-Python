#ifndef COMMANDS_H_
#define COMMANDS_H_

// C includes
#include <stdint.h>
#include <string.h>

// Project includes
#include "DigitalPortsManager.h"
#include "errors.h"

enum CMD_OPCODES {
  START_CONFIG = 1,
  END_CONFIG = 2,
  ACK = 3,
  ERROR = 4,
  CONFIG_DIGITAL_PORT = 10,
  WRITE_DIGITAL_PORT = 20,
  READ_DIGITAL_PORT = 21
};

struct Command {
  Command() 
    : opcode(0)
    , size(0) {
    memcpy(payload, 0, 64);
  }
    
  uint8_t opcode;
  uint8_t size;
  uint8_t payload[32];
};

typedef uint8_t (*CmdFuncPtr)(Command* cmd);
extern int G_ERROR_LED;
bool on_config = false;
DigitalPortManager portManager;

// Function Declarations
void setCmdFuncPtr();
uint8_t startConfigCommand(Command* cmd);
uint8_t endConfigCommand(Command* cmd);
uint8_t configDigitalPortCommand(Command* cmd);
uint8_t writeDigitalPortCommand(Command* cmd);
bool createACKCommand(Command* cmd, uint8_t opcode);
bool validCommand(uint8_t opcode);

// Initialize by default all the callbacks to NULL
CmdFuncPtr gCmdFuncPtr[32] = {};


/** Definitions **/
void setCmdFuncPtr() {
  gCmdFuncPtr[START_CONFIG] = startConfigCommand;
  gCmdFuncPtr[END_CONFIG] = endConfigCommand;
  gCmdFuncPtr[CONFIG_DIGITAL_PORT] = configDigitalPortCommand;
  gCmdFuncPtr[WRITE_DIGITAL_PORT] = writeDigitalPortCommand;
}


uint8_t startConfigCommand(Command* cmd) {
  on_config = true;
  return NO_ERROR;
}


uint8_t endConfigCommand(Command* cmd) {
  on_config = false;
  return NO_ERROR;
}


uint8_t configDigitalPortCommand(Command* cmd) {
  if (not on_config) {
    return CONFIG_WHILE_MEASURE;
  }
  
  uint8_t ports = cmd->size - 2;
  uint8_t i = 0;

  int8_t port = 0;
  uint8_t mode = 0;
  uint8_t error_code = 0;
  for (; i < ports; i+=2) {
    port = *(cmd->payload + i);
    mode = *(cmd->payload + i + 1);
    error_code = portManager.setPort(port, mode);
    if (error_code) {
      return error_code;
    }

    if (mode == PIN_INPUT) {
      pinMode(port, INPUT);
    }
    else if (mode == PIN_OUTPUT) {
      pinMode(port, OUTPUT);  
    }
    else {
      // TODO: Can I deconfigure a port?
    }
  }

  return NO_ERROR;
}


uint8_t writeDigitalPortCommand(Command* cmd) {
  if (on_config) {
    return MEASURE_WHILE_ON_CONFIG;
  }
  
  uint8_t ports = cmd->size - 2;
  uint8_t i = 0;

  int8_t port = 0;
  uint8_t value = 0;
  PinMode mode = PIN_NOT_CONFIGURED;
  uint8_t error_code = 0;
  
  for (; i < ports; i+=2) {
    port = *(cmd->payload + i);
    value = *(cmd->payload + i + 1);
    error_code = portManager.getPinMode(port, &mode);
    if (error_code) {
      return error_code;
    }

    if (mode != PIN_OUTPUT) {
      return WRITING_ON_MISCONFIGURE_PORT;
    }

    digitalWrite(port, value);
  }

  return NO_ERROR;
}


bool createACKCommand(Command* cmd, uint8_t opcode) {
  cmd->opcode = ACK;
  cmd->size = 4;
  if (validCommand(opcode)) {
    *(cmd->payload) = opcode;
    // WORKAROUND: Padding so ACK and ERROR packages has the same size
    *(cmd->payload + 1) = 0;
    return true;
  }

  return false;
}


bool createErrorCommand(Command* cmd, uint8_t opcode, uint8_t error_code) {
  cmd->opcode = ERROR;
  cmd->size = 4;

  if (not validCommand(opcode)) {
    return false;
  }

  // TODO: Check error code
  *(cmd->payload) = opcode;
  *(cmd->payload + 1) = error_code;
  return true;
}


bool validCommand(uint8_t opcode) {
  return gCmdFuncPtr[opcode] != NULL;
}


#endif // COMMANDS_H_

