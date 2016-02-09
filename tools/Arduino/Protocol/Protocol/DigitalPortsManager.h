#ifndef DIGITAL_PORT_MANAGER_H_
#define DIGITAL_PORT_MANAGER_H_

#include "errors.h"

#define PORT_MAP_ARRAY_SIZE 10

enum PinMode {
  PIN_INPUT = 1,
  PIN_OUTPUT = 2,
  PIN_NOT_CONFIGURED = 3
};


class DigitalPortManager {
public:
  DigitalPortManager() {
    // Set the digital ports availables at Arduino One (2, 3, 4, 5, 6, 7, 8, 9, 10)
    uint8_t i = 0;
    for (; i < 9; ++i) {
      (portMap + i)->number = i + 2;
      (portMap + i)->mode = PIN_NOT_CONFIGURED;    
    }
  }


  int8_t setPort(int8_t port, uint8_t mode) {
    int8_t portIndex = this->getPortIndex(port);
    if (portIndex > 0) {
      // The port exists. Configure it
      if (not this->validPinMode(mode)) {
        return INVALID_DIGITAL_PORT_MODE;
      }
      
      (portMap + portIndex)->mode = (PinMode) mode;
      return NO_ERROR;
    }

    return INVALID_DIGITAL_PORT_NUMBER;
  }


  int8_t getPinMode(int8_t portNumber, PinMode* mode) {
    int8_t portIndex = getPortIndex(portNumber);
    if (portIndex == -1) {
      return INVALID_DIGITAL_PORT_NUMBER;
    }
    
    *mode = (portMap + portIndex)->mode;
    return NO_ERROR;
  }


private:
  bool validPinMode(int8_t mode) {
    return mode == PIN_INPUT || 
           mode == PIN_OUTPUT || 
           mode == PIN_NOT_CONFIGURED;
  }

  
  int8_t getPortIndex(int8_t portNumber) {
    if (portNumber <= 0) {
      return -1;
    }
    
    uint8_t i = 0;
    int8_t portAnalized = 0;
    for (; i < PORT_MAP_ARRAY_SIZE; ++i) {
      portAnalized = (portMap + i)->number;
      if (portAnalized > 0) {
        if (portAnalized == portNumber) {
          return i;
        }
      }
    }

    return -1;
  }
  

private:
  struct DigitalPins {
    DigitalPins()
      : number(-1)
      , mode(PIN_NOT_CONFIGURED) {}
      
    int8_t number;
    PinMode mode;
  };
  
private:
  DigitalPins portMap[PORT_MAP_ARRAY_SIZE];
};

#endif // DIGITAL_PORT_MANAGER_H_

