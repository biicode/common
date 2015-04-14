import unittest
from biicode.common.edition.parsing.python.py_parser import PythonParser
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.model.declare.python_declaration import PythonDeclaration

code = """#biicode
from biicode.hola.dos import espinte as pocoyo#es biicode nena
from biicode.hola.dos import chorizos
\"\"\"
wololololololo
\"\"\"
import sys
def test():
    import biicode.hola.dos   as   wololo
edad = 0
while edad < 18:
    edad = edad + 1
print 'Felicidades, tienes ' + str(edad)
#bii://wololo
"""

fileData = """import sys
from re import match
#import os
import myBlock
from functions import LeerLista
\"\"\"
import comments
\"\"\"
import sys
import user.hive

var1 = 1
var2 = 2

def fff(a):
    print a

class foo(object):

    #bii://user1/module1/user1
    def __init__(self):
        self.var = None


#bii://user2/module2/file2
if __name__ == 'main':
    print "Hello world!!!"
    print "#bii://medaigual/jhdjs"
"""

buggy_code = r'''#!/usr/bin/env python
#
# Script to sort the game controller database entries in SDL_gamecontroller.c

import re


filename = "SDL_gamecontrollerdb.h"
input = open(filename)
output = open(filename + ".new", "w")
parsing_controllers = False
controllers = []
controller_guids = {}
split_pattern = re.compile(r'([^"]*")([^,]*,)([^,]*,)([^"]*)(".*)')

def save_controller(line):
    global controllers
    match = split_pattern.match(line)
    entry = [ match.group(1), match.group(2), match.group(3) ]
    bindings = sorted(match.group(4).split(","))
    if (bindings[0] == ""):
        bindings.pop(0)
    entry.extend(",".join(bindings) + ",")
    entry.append(match.group(5))
    controllers.append(entry)

def write_controllers():
    global controllers
    global controller_guids
    for entry in sorted(controllers, key=lambda entry: entry[2]):
        line = "".join(entry) + "\n"
        if not line.endswith(",\n") and not line.endswith("*/\n"):
            print "Warning: '%s' is missing a comma at the end of the line" % (line)
        if (entry[1] in controller_guids):
            print "Warning: entry '%s' is duplicate of entry '%s'" % (entry[2], controller_guids[entry[1]][2])
        controller_guids[entry[1]] = entry

        output.write(line)
    controllers = []
    controller_guids = {}

for line in input:
    if ( parsing_controllers ):
        if (line.startswith("{")):
            output.write(line)
        elif (line.startswith("#endif")):
            parsing_controllers = False
            write_controllers()
            output.write(line)
        elif (line.startswith("#")):
            print "Parsing " + line.strip()
            write_controllers()
            output.write(line)
        else:
            save_controller(line)
    else:
        if (line.startswith("static const char *s_ControllerMappings")):
            parsing_controllers = True

        output.write(line)

output.close()
print "Finished writing %s.new" % filename
'''


class TestPythonASTParser(unittest.TestCase):
    def test_bug(self):
        py = PythonParser()
        py.parse(buggy_code)
        obtained = [ref.name for ref in py.imports]
        obteined2 = [ref.name for ref in py.references]
        expected = ['import re']
        self.assertEqual(expected, obtained)
        expected2 = []
        self.assertEqual(expected2, obteined2)

    def test_parserPythonImports(self):
        py = PythonParser()
        py.parse(code)
        obtained = [ref.name for ref in py.imports]
        expected = ['from biicode.hola.dos import espinte as pocoyo',
                    'from biicode.hola.dos import chorizos',
                    'import sys', 'import biicode.hola.dos as wololo']
        self.assertEqual(expected, obtained)

    def test_parserPythonComments(self):
        py = PythonParser()
        py.parse(code)
        obteined = [ref.name for ref in py.references]

        expected = ['bii://wololo']
        self.assertEqual(expected, obteined)

    def test_parserPythonItems(self):
        py = PythonParser()
        py.parse(fileData)
        obtained = [ref.name for ref in py.imports]
        obteined2 = [ref.name for ref in py.references]

        expected = ['import sys', 'from re import match', 'import myBlock', 'from functions import LeerLista', 'import sys','import user.hive']
        self.assertEqual(expected, obtained)

        expected2 = ['bii://user1/module1/user1', 'bii://user2/module2/file2']
        self.assertEqual(expected2, obteined2)

    def test_python_c_include(self):
        code = r'''
import biipyc
import my_block
lib = link_clib("user/block/test.h")
some_var = test("user/block/cosa.h")
value = 3
libd = biipyc.link_clib("user/block/test2.h")'''

        py = PythonParser()
        py.parse(code)
        obtained_explicit_decs = py.explicit_declarations
        expected_explicit_decs = [CPPDeclaration("user/block/test.h"),
                                  CPPDeclaration("user/block/test2.h"),
                                  PythonDeclaration("import my_block"),
                                  PythonDeclaration("import biipyc")]

        self.assertItemsEqual(expected_explicit_decs, obtained_explicit_decs)
        self.assertTrue(py.has_main_function())

if __name__ == "__main__":
    unittest.main()