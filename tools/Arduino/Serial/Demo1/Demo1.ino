#include <TimerOne.h>
#include "CommandProcessor.h"

char value[255];
int led = 13;
volatile bool firstTime = true;
volatile bool isrJumped = false;
void timerIsr();
CommandProcessor cmdProcessor(timerIsr);

void timerIsr() {
  if (not firstTime) {
    Timer1.detachInterrupt();
    firstTime = true;
    cmdProcessor.finishProcessingCommand();
    digitalWrite(led, LOW);
  }
  else {
    firstTime = false;
    digitalWrite(led, HIGH);
  }
}


void setup() {
  Serial.begin(115200);
  // Pin 13 has an LED connected on most Arduino boards
  pinMode(led, OUTPUT);
  digitalWrite(led, LOW);

  // set a timer of length 1000000 microseconds 
  // (or 0.1 sec - or 10Hz => the led will blink 5 times, 5 cycles of on-and-off, per second)
  Timer1.initialize(100000);
}

void loop() {
  cmdProcessor.readCommand();
  int cmd = cmdProcessor.processCommand();

  if (cmd == CommandProcessor::ISR) {
    Serial.write(cmdProcessor.sensorValue());
  }
}

