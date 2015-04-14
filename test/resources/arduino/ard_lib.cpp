#if ARDUINO >= 100
    #include "Arduino.h"
#else
    #include "WProgram.h"
#endif

#include "%INO%/hello/blink_lib.h"
#include "ard_lib.h"

void blink_setup2(uint8_t pin) {
  blink_setup(pin);     
}


void blink2(unsigned long duration, uint8_t pin) {
  blink(duration, pin);
}