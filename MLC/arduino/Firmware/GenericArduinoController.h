/*
  GenericArduinoController.h - Library for remote Arduino control
  Released into the public domain.
*/
#ifndef GenericArduinoController_h
#define GenericArduinoController_h

#include "Arduino.h"

// defines ahorran ROM... aunque nos sobra de eso XD -- Verificar que los const vayan a la rom!
const uint8_t ANALOG_PRECISION_CMD  = 0x01;
const uint8_t ADD_INPUT_PIN_CMD     = 0x02;
const uint8_t ADD_OUTPUT_PIN_CMD    = 0x03;
const uint8_t SET_PIN_MODE_CMD      = 0x04;
const uint8_t SET_REPORT_MODE_CMD   = 0x05;
const uint8_t ANALOG_WRITE          = 0x06;
const uint8_t ACTUATE_CMD           = 0xF0;
const uint8_t ACTUATE_RESPONSE      = 0xF1;
const uint8_t PROTOCOL_VERSION      = 0xF2;
const uint8_t VERSION_RESPONSE      = 0xF3;
const uint8_t RESET_PINS            = 0xFE;

typedef enum ReportModes {average, bulk, rt};

class GenericArduinoController
{
  public:
    GenericArduinoController(Stream &stream);

    void handle_commands(); 

    void add_handler(uint8_t handler_id, int (*handler)(GenericArduinoController* this_, uint32_t &buff_len, const char*));

  private:
    Stream &stream_;

    uint8_t REPORT_READ_COUNT;
    uint8_t REPORT_READ_DELAY;
    ReportModes REPORT_MODE;
    uint8_t INPUT_PORTS[129]; // Port count in first position
    uint8_t ANALOG_PINS_COUNT;
    uint8_t DIGITAL_PINS_COUNT;

    int (*executor[255])(GenericArduinoController*, uint32_t &buff_len, const char*);

    // NULL operation
    static int not_implemented(GenericArduinoController* this_, uint32_t &buff_len, const char* data);
   
    /**
     * PROTOCOL_VERSION 0x07 0x00 0x00 0x00 0x03 X . Y
     */ 
    static int protocol_version(GenericArduinoController* this_, uint32_t &buff_len, const char* data);

    /**
     * ANALOG_WRITE: 0x06 0x00 0x00 0x00 0x03 [PIN] [H_VALUE][L_VALUE]
     */
    static int analog_write(GenericArduinoController* this_, uint32_t &buff_len, const char* data);

    /**
     *   ANALOG_PRECISION: 0x01 0x00 0x00 0x00 0x01 [BITS]
     */
    static int set_analog_precision(GenericArduinoController* this_, uint32_t &buff_len, const char* data);

    /**
    *   PIN_MODE: 0x04 0x00 0x00 0x00 0x02 [PIN] [MODE]
    */
    static int set_pin_mode(GenericArduinoController* this_, uint32_t &buff_len, const char* data);
    
    /**
    *   REPORT_MODE: 0x05 0x00 0x00 0x00 0x03 [MODE] [READ_COUNT] [READ_DELAY]
    */
    static int set_report_mode(GenericArduinoController* this_, uint32_t &buff_len, const char* data);
    
    /**
    *   ANALOG_INPUT: 0x02 0x00 0x00 0x00 0x01 [PORT]
    */
    static int set_analog_input(GenericArduinoController* this_, uint32_t &buff_len, const char* data);
    
    /**
    *   RESET: 0xFF 0x00 0x00 0x00 0x00
    */
    static int reset(GenericArduinoController* this_, uint32_t &buff_len, const char* data);
    
    /**
    *   ANALOG_OUTPUT: 0x03 0x01 0x00 0x00 0x00 [PORT]
    */
    static int set_analog_output(GenericArduinoController* this_, uint32_t &buff_len, const char* data);
    
    /**
    *   ACTUATE: 0xF0 [DATA_LEN] [PIN_A] [VALUE_PIN_A] ... [PIN_N] [VALUE_PIN_N]
    */
    static int actuate(GenericArduinoController* this_, uint32_t &buff_len, const char* data);

};

#endif
