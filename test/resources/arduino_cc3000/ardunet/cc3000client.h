/*
 * cc3000client.h Wrapper class conforming to WiFiClient interface that wraps the
 * CC3000 and Adafruit_CC3000_Client
 *
 *  Created on: 31/03/2014
 *      Author: drodri
 */

#ifndef CC3000CLIENT_H_
#define CC3000CLIENT_H_

//Now it is working with the biicode version of wificlient, because of some linking errors
//of cmake if not including wifi.h. Can produce linking errors if your program include wifi
#include "WiFi.h"
#include "WiFiClient.h"
#include "%INO%/cc3000_library/adafruit_cc3000.h"
#include "Stream.h"
 

class CC3000Client: public WiFiClient {
public:
	CC3000Client(Adafruit_CC3000& cc, Stream& stream=Serial);
	virtual ~CC3000Client();

	virtual int connect(IPAddress ip, uint16_t port);
	virtual int connect(const char *host, uint16_t port);
	virtual uint8_t connected();
	virtual int available();
	virtual void stop();
	virtual void flush();
	virtual int peek();
	virtual int read();
	virtual size_t write(uint8_t v);
	virtual size_t write(const uint8_t *buf, size_t size);
	virtual int read(uint8_t *buf, size_t size);
	virtual operator bool();

private:
	Adafruit_CC3000& cc3000;
	Adafruit_CC3000_Client client;
	bool peeked;
	int peeked_byte;
	Stream& stream;
};

#endif /* CC3000CLIENT_H_ */
