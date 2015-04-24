from biicode.common.model.cells import SimpleCell
from biicode.common.model.bii_type import CPP
from biicode.common.edition.processors.arduino_entry_points import ArduinoEntryPointProcesor
from biicode.common.model.blob import Blob
from biicode.common.model.content import Content
from biicode.common.edition.parsing.cpp.drl_parser import DRLCPPParser
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.resource import Resource
from biicode.common.model.brl.block_name import BlockName
from mock import Mock
from biicode.common.test.bii_test_case import BiiTestCase

header = '''#pragma once

#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif


class Blink {
public:
    void blink_setup(int led, int interval_ms);
    void blink_loop();

private:
    int ledState;            // ledState used to set the LED
    int ledPin;
};
'''

implementation = '''
#include "blink.h"

void Blink::blink_setup(int led, int interval_ms) {
    ledState = LOW;
    previousMillis = 0;

    interval = 1000;
    ledPin = 13;
    pinMode(ledPin, OUTPUT);
}

void Blink::blink_loop() {

    unsigned long currentMillis = millis();
    ledState = HIGH;
    digitalWrite(ledPin, ledState);
 }
'''

main = """#include "blink.h"

Blink my_blink;

void setup() {
  my_blink.blink_setup(13, 1000); //pin = 13, interval = 1000 ms,
}

void loop(){
  my_blink.blink_loop();
  //you can do other things here, blink won't block
}
"""


class ArduinoEntryPointTest(BiiTestCase):

    def test_find_mains(self):
        '''basic check that header is implemented by source'''
        resources = {'blink.h': Resource(SimpleCell('usr/block/blink.h', CPP),
                                       Content(id_=None, load=Blob(header), parser=DRLCPPParser())),
                   'blink.cpp':  Resource(SimpleCell('usr/block/blink.cpp', CPP),
                                        Content(id_=None, load=Blob(implementation), parser=DRLCPPParser())),
                   'mainblink.cpp': Resource(SimpleCell('usr/block/mainblink.cpp', CPP),
                                             Content(id_=None, load=Blob(main), parser=DRLCPPParser()))}
        block_holder = BlockHolder(BlockName('user/block'), resources)
        for r in resources.itervalues():
            r.content.parse()
            r.content.updated = False
        processor = ArduinoEntryPointProcesor()
        processor.do_process(block_holder, Mock())
        mainblink = block_holder['mainblink.cpp'].cell
        content = block_holder['mainblink.cpp'].content
        self.assertTrue(mainblink.hasMain)
        self.assertFalse(content.updated)
        self.assertFalse(content.blob_updated)
