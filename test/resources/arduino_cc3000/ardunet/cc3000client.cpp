#include "cc3000client.h"


CC3000Client::CC3000Client(Adafruit_CC3000& cc, Stream& stre) :
		cc3000(cc), peeked(false), stream(stre), peeked_byte(0) {
}
CC3000Client::~CC3000Client() {
}

int CC3000Client::connect(IPAddress ip, uint16_t port) {
	//it seems that the IP to adafruit is reversed
	IPAddress ip2(ip[3], ip[2], ip[1], ip[0]);
	client = cc3000.connectTCP((uint32_t) ip2, port);
	peeked = false;
	if (client.connected())
		return 1;
	return 0;
}
int CC3000Client::connect(const char *host, uint16_t port) {
	uint32_t ip = 0;
	if (!cc3000.getHostByName((char*) host, &ip)) {
		stream.println(F("Couldn't resolve!"));
		return 0;
	}
	client = cc3000.connectTCP(ip, port);
	peeked = false;
	if (client.connected()) {
		return 1;
	}
	return 0;
}
uint8_t CC3000Client::connected() {
	return (uint8_t) client.connected();
}
int CC3000Client::available() {
	if(peeked)
		return 1;
	return (int) client.available();
}
void CC3000Client::stop() {
	peeked = false;
	flush();
	while (client.connected()){
		client.close();
		delay(10);
	}
}
void CC3000Client::flush() {
	peeked = false;
	while (connected() && available())
		read();
}
int CC3000Client::peek() {
	if (!peeked) {
		if (available()) {
			peeked_byte = read();
			peeked = true;
		} else
			return -1;
	}
	return peeked_byte;

}
int CC3000Client::read() {
	if (peeked) {
		peeked = false;
		return peeked_byte;
	}
	return (int) client.read();
}
size_t CC3000Client::write(uint8_t v) {
	return (size_t) client.write(v);
}
size_t CC3000Client::write(const uint8_t *buf, size_t size) {
	return client.write(buf, size);
}
int CC3000Client::read(uint8_t *buf, size_t size) {
	if(peeked){
		buf[0]=peeked_byte;
		peeked=false;
		return client.read(buf+1, size-1);
	}
	return client.read(buf, size);
}
CC3000Client::operator bool() {
	stream.println("Error, bool() not implemented");
	return true;
}

