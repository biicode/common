#include "Arduino.h"
#include <string.h>
#include "cc3000client.h"


void http_get(Adafruit_CC3000_Client& www, char website[], char webpage[],
		int timeout, Stream& stream) {
	if (www.connected()) {
		www.fastrprint(F("GET "));
		www.fastrprint(webpage);
		www.fastrprint(F(" HTTP/1.1\r\n"));
		www.fastrprint(F("Host: "));
		www.fastrprint(website);
		www.fastrprint(F("\r\n"));
		www.fastrprint(F("\r\n"));
		//www.println();
	} else {
		stream.println(F("Connection failed cc"));
		return;
	}

	stream.println(F("-------------------------------------"));

	/* Read data until either the connection is closed, or the idle timeout is reached. */
	unsigned long lastRead = millis();
	while (www.connected() && (millis() - lastRead < timeout)) {
		while (www.available()) {
			char c = www.read();
			stream.print(c);
			lastRead = millis();
		}
	}
	stream.println(F("-------------------------------------"));
}
void http_get(Client& www, char website[], char webpage[],
		int timeout, Stream& stream) {
	if (www.connected()) {
		int n = www.print("GET ");
		www.print(webpage);
		www.print(" HTTP/1.1\r\n");
		www.print("Host: ");
		www.print(website);
		www.print("\r\n");
		www.print("\r\n");
		//www.println();
	} else {
		stream.println(F("Connection failed get"));
		return;
	}

	stream.println(F("-------------------------------------"));

	/* Read data until either the connection is closed, or the idle timeout is reached. */
	unsigned long lastRead = millis();
	while (www.connected() && (millis() - lastRead < timeout)) {
		while (www.available()) {
			char c = www.read();
			stream.print(c);
			lastRead = millis();
		}
	}
	stream.println(F("-------------------------------------"));
}
