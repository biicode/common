#include <stdint.h>

/**
 * Setup for blinking.
 *
 * @param pin - pin number
 **/
void blink_setup2(uint8_t pin=13);


/**
 * Blink a single time for the specified duration.
 *
 * @param duration - duration in miliseconds
 * @param pin      - pin number
 **/
void blink2(unsigned long duration, uint8_t pin=13);