#ifndef COMMAND_PROCESSOR_H_
#define COMMAND_PROCESSOR_H_

#include "commands.h"

class CommandProcessor {
public:
  /**
   * Return a reference to the command read. If there was an error, NULL is returned
   * THE FUNCTION IS NOT REENTRANT. Every time the function is invoked, the buffer 
   * is overriden
   */
  Command* readCommand() {
    int8_t index = 0;
  
    // First, read opcode and size of the commands
    Serial.readBytes((char*)&cmd_, 2);
  
    if (not *(gCmdFuncPtr + cmd_.opcode)) {
      // Invalid command      
      return NULL;
    }
  
    // Valid command, read the entire command
    int8_t remainder = cmd_.size - 2;
    if (remainder > 0) {
      Serial.readBytes((char*) cmd_.payload, remainder);
    }
  
    return &cmd_;
  }

private:
  Command cmd_;
};

#endif // COMMAND_PROCESSOR_H_

