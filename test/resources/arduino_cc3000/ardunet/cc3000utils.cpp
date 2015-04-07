#include "cc3000utils.h"


bool startConnection(Adafruit_CC3000& cc3000, char ssid[], char pass[], uint8_t sec, Stream& stream){
	/* Initialise the module */
	stream.println(F("\nInitializing..."));
	if (!cc3000.begin()) {
		stream.println(F("Couldn't begin()! Check your wiring?"));
		return false;
	}

	if (!cc3000.connectToAP(ssid, pass, sec)) {
		stream.println(F("Failed!"));
		return false;
	}

	/* Wait for DHCP to complete */
	stream.println(F("Request DHCP"));
	while (!cc3000.checkDHCP()) {
		delay(100); // ToDo: Insert a DHCP timeout!
	}

	/* Display the IP address DNS, Gateway, etc. */
	while (!displayConnectionDetails(cc3000)) {
		delay(1000);
	}

	return true;
}

bool displayConnectionDetails(Adafruit_CC3000& cc3000, Stream& stream){
  uint32_t ipAddress, netmask, gateway, dhcpserv, dnsserv;

  if(!cc3000.getIPAddress(&ipAddress, &netmask, &gateway, &dhcpserv, &dnsserv))
  {
	  stream.println(F("Unable to retrieve the IP Address!\r\n"));
	  return false;
  }
  else
  {
	  stream.print(F("\nIP Addr: ")); cc3000.printIPdotsRev(ipAddress);
	  stream.print(F("\nNetmask: ")); cc3000.printIPdotsRev(netmask);
	  stream.print(F("\nGateway: ")); cc3000.printIPdotsRev(gateway);
	  stream.print(F("\nDHCPsrv: ")); cc3000.printIPdotsRev(dhcpserv);
	  stream.print(F("\nDNSserv: ")); cc3000.printIPdotsRev(dnsserv);
	  stream.println();
	  return true;
  }
}

void listSSIDResults(Adafruit_CC3000& cc3000, Stream& stream)
{
  uint8_t valid, rssi, sec, index;
  char ssidname[33];

  index = cc3000.startSSIDscan();

  stream.print(F("Networks found: ")); stream.println(index);
  stream.println(F("================================================"));

  while (index) {
    index--;

    valid = cc3000.getNextSSID(&rssi, &sec, ssidname);

    stream.print(F("SSID Name    : ")); stream.print(ssidname);
    stream.println();
    stream.print(F("RSSI         : "));
    stream.println(rssi);
    stream.print(F("Security Mode: "));
    stream.println(sec);
    stream.println();
  }
  stream.println(F("================================================"));

  cc3000.stopSSIDscan();
}
