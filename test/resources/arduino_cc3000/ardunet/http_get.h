/*
 * cc3000client.h Wrapper class conforming to WiFiClient interface that wraps the
 * CC3000 and Adafruit_CC3000_Client
 *
 *  Created on: 31/03/2014
 *      Author: drodri
 */

#ifndef HTTP_GET_INCLUDED_H_
#define HTTP_GET_INCLUDED_H_

#include "WiFi.h"
#include "WiFiClient.h"
#include <%INO%/cc3000_library/adafruit_cc3000.h>
#include "Stream.h"


/**Convenience method that perform a http GET call using either a Adafruit client or the
 * wrapper class
 */
void http_get(Adafruit_CC3000_Client& www, char website[], char webpage[],
				int timout=1000, Stream& stream=Serial);
void http_get(Client& www, char website[], char webpage[],
				int timout=1000, Stream& stream=Serial);

#endif /* CC3000CLIENT_H_ */
