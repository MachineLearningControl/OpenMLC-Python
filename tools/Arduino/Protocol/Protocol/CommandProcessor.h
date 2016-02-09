#ifndef COMMAND_PROCESSOR_H_
#define COMMAND_PROCESSOR_H_

// Project includes
#include "commands.h"
#include "errors.h"
#include "util.h"

extern int G_ERROR_LED;

class CommandProcessor {
public:
  /**
   * Return a reference to the command read. If there was an error, NULL is returned
   * THE FUNCTION IS NOT REENTRANT. Every time the function is invoked, the buffer 
   * is overriden
   */
  Command* readCommand() { 
    // First, read opcode and size of the commands
    while (Serial.available() != 2) {}
    
    // Read the command opcode and size
    cmd_.opcode = Serial.read();
    cmd_.size = Serial.read();

    if (not validCommand(cmd_.opcode)) {
      createErrorCommand(&write_cmd_, cmd_.opcode, INVALID_OPCODE);
      this->sendCommand();
      blinkVariable(G_ERROR_LED, INVALID_OPCODE);
      // Invalid command
      return NULL;
    }
  
    // Valid command, read the entire command
    int8_t remainder = cmd_.size - 2;
    if (remainder < 0) {
      // Buggy behaviour
      digitalWrite(G_ERROR_LED, HIGH);
      return NULL;
    }
    else if (remainder == 0) {
      return &cmd_;
    }

    // ACK the first part of the command
    createACKCommand(&write_cmd_, cmd_.opcode);
    this->sendCommand();

    while (Serial.available() < remainder) {}
    uint8_t i = 0;
    char c = 0;
    for (; i < remainder; ++i) {
      c = Serial.read();
      memcpy(cmd_.payload + i, &c, 1);
    }

    return &cmd_;
  }

  uint8_t processCommand(Command* cmd) {
    digitalWrite(G_ERROR_LED, LOW);
    int8_t error_code = gCmdFuncPtr[cmd->opcode](cmd);
    if (error_code) {
      createErrorCommand(&write_cmd_, cmd->opcode, error_code);
      this->sendCommand();
    }
    else {
      createACKCommand(&write_cmd_, cmd->opcode);
      this->sendCommand();
    }

    return error_code;
  }

private:
  void sendCommand() {
    Serial.write((char*) &write_cmd_, write_cmd_.size);
  }


private:
  Command cmd_;
  Command write_cmd_;
};

#endif // COMMAND_PROCESSOR_H_

