#ifndef UTIL_H_
#define UTIL_H_

void blinkVariable(uint8_t led, uint8_t number_blinks, uint32_t delay_time = 200) {
  while (number_blinks) {
    --number_blinks;
    digitalWrite(G_ERROR_LED, HIGH);
    delay(delay_time);
    digitalWrite(G_ERROR_LED, LOW);
    delay(delay_time);
  }

  delay(delay_time*10);
}

#endif // UTIL_H_
