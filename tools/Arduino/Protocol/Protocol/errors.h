#ifndef ERRORS_H_
#define ERRORS_H_

enum ERROR_CODES {
  NO_ERROR = 0,
  MEASURE_WHILE_ON_CONFIG = 5, // A read or write port command arrived while we are in configuration mode
  CONFIG_WHILE_MEASURE = 6, // A config port command arrived while we are reading/writing ports
  INVALID_OPCODE = 7, // Opcode received is not valid
  INVALID_DIGITAL_PORT_NUMBER = 8, // A config port command arrived but the port number is not valid
  INVALID_DIGITAL_PORT_MODE = 9, // A config port command arrived but the port mode doesn't exists
  WRITING_ON_MISCONFIGURE_PORT = 10 // Writing on a port not configure as OUTPUT
};

#endif // ERRORS_H_
