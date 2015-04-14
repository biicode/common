#include "pretty.h"
#include "hello.h"

%INCLUDE_EXTERNAL_PRETTY%

void prettyLoop%BLOCKNAME%(){
	Serial.println("*************");
	helloLoop%BLOCKNAME%();
	Serial.println("*************");

	%CALL_EXTERNAL_PRETTY%
 }
