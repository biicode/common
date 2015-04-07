/*
  Blink
  Turns on an LED on for one second, then off for one second, repeatedly.
  Example uses a static library to show off generate_arduino_library().
 
  This example code is in the public domain.
 */
#if ARDUINO >= 100
    #include "Arduino.h"
#else
    #include "WProgram.h"
#endif

#include "%INO%/hello3/ard_lib.h"

void setup() {                
    blink_setup2(); // Setup for blinking
}

void loop() {
    blink2(1000); // Blink for a second
}
