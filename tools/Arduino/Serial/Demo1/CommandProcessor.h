#include <TimerOne.h>

class CommandProcessor {
public:
  enum CMD_TYPE {
    ISR = 1, 
    SENSOR = 2,
    ERROR = 255
  };

  class Command {
  public:
    void reset() {
      size = 0;
    }
    
  public:
    char command[255];
    int size;
  };

  typedef void (*ISRFunction)() ;
  
public:
  CommandProcessor(ISRFunction isr, const char delimiter = '|') 
    : _isr(isr) 
    , _delim(delimiter)
    , _finishcmdProcessing(false) {}
    
  void readCommand() {
    char c = 0;
    int index = 0;
    _finishcmdProcessing = false;
    _cmd.reset();
    
    while (c != '\n') {
      if (Serial.available()) {
        c = Serial.read();
      }
      else {
        continue;
      }
      
      if (c != '\n') {
        *(_cmd.command + index) = c;
        ++index;
      }
    }

    ++index;
    *(_cmd.command + index) = '\0';
    _cmd.size = index;
  }

  int processCommand() {
    if (not _cmd.size) {
      return ERROR;
    }

    char* origin = _cmd.command;
    char* delim = strchr(_cmd.command, '|');
    *delim = '\0';
    int opcode = atoi(origin);
    long isrPeriod = 0;

    switch (opcode) {
      case ISR:
        origin = delim + 1;
        delim = strchr(origin, '|');
        *delim = '\0';
        isrPeriod = atol(origin);
        strcpy(_sensorValue, delim + 1);
        *(_sensorValue + strlen(_sensorValue)) = '\n';
        *(_sensorValue + strlen(_sensorValue) + 1) = '\0';
     
        Timer1.setPeriod(isrPeriod);
        Serial.end();
        Timer1.attachInterrupt(_isr);

        // FIXME: Do something else than loop
        while (not _finishcmdProcessing) {}
        Serial.begin(115200);
        return ISR;
        break;
       default:
         // Invalid command received
         break;
    }
  }

  const char* sensorValue() const {
    return _sensorValue;
  }
  
  /**
   * Methods only used in interruptions
   */
  void finishProcessingCommand() {
    _finishcmdProcessing = true;
  }
  
private:
  ISRFunction _isr;
  const char _delim;
  volatile bool _finishcmdProcessing;
  Command _cmd;
  char _sensorValue[255];
};


