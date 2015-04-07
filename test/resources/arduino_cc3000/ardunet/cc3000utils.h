/*
 * cc3000client.h Wrapper class conforming to WiFiClient interface that wraps the
 * CC3000 and Adafruit_CC3000_Client
 *
 *  Created on: 31/03/2014
 *      Author: drodri
 */

#ifndef CC3000UTILS_H_
#define CC3000UTILS_H_

#include "%INO%/cc3000_library/adafruit_cc3000.h"

bool startConnection(Adafruit_CC3000& cc3000, char ssid[], char pass[], uint8_t sec, Stream& stream=Serial);
bool displayConnectionDetails(Adafruit_CC3000& cc3000, Stream& stream=Serial);
void listSSIDResults(Adafruit_CC3000& cc3000, Stream& stream=Serial);

#endif /* CC3000CLIENT_H_ */
