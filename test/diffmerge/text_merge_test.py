import unittest
from biicode.common.diffmerge.text_merge import three_way_merge_text


class MergeTest(unittest.TestCase):

    def test_other_change(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        source = base
        for line in base.splitlines():
            target = base.replace(line, line + '*')
            result, collision = three_way_merge_text(base, source, target)
            self.assertEquals(target, result)
            self.assertFalse(collision)

    def test_base_change(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        target = base
        for line in base.splitlines():
            source = base.replace(line, line + '*')
            result, collision = three_way_merge_text(base, source, target)
            self.assertEquals(source, result)
            self.assertFalse(collision)

    def test_base_deletion(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        target = base
        for line in base.splitlines():
            source = base.replace(line + '\n', "")
            result, collision = three_way_merge_text(base, source, target)
            self.assertEquals(source, result)
            self.assertFalse(collision)

    def test_other_deletion(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        source = base
        for line in base.splitlines():
            target = base.replace(line + '\n', "")
            result, collision = three_way_merge_text(base, source, target)
            self.assertEquals(target, result)
            self.assertFalse(collision)

    def test_source_insertion(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        source = 'zero\none\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        target = base
        result, collision = three_way_merge_text(base, source, target)
        self.assertEquals(source, result)
        self.assertFalse(collision)

    def test_middle_insertion(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        source = 'one\ntwo\nthree\nten\nfour\nfive\nsix\nseven\n'
        target = base
        result, collision = three_way_merge_text(base, source, target)
        self.assertEquals(source, result)
        self.assertFalse(collision)

    def test_both_insertions(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        target = 'zero\none\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        source = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\neight\n'
        result, collision = three_way_merge_text(base, source, target)
        self.assertEquals('zero\none\ntwo\nthree\nfour\nfive\nsix\nseven\neight\n', result)
        self.assertFalse(collision)

    def test_combined_change(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\nocho\nnueve\ndiez\n'
        lines = base.splitlines()
        for i in range(0, 4):
            l1 = lines[i]
            l2 = lines[len(lines) - i - 2]
            source = base.replace(l1, l1 + " S")
            target = base.replace(l2, l2 + " T")
            result, collision = three_way_merge_text(base, source, target)
            expected = source.replace(l2, l2 + " T")
            self.assertEquals(expected, result)
            self.assertFalse(collision)

    def test_combined_change_add(self):
        base = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        lines = base.splitlines()
        for i in range(0, 3):
            l1 = lines[i]
            l2 = lines[len(lines) - i - 1]
            source = base.replace(l1, l1 + " S\nS\nS")
            target = base.replace(l2, l2 + " T\nT\nT")
            result, collision = three_way_merge_text(base, source, target)
            expected = source.replace(l2, l2 + " T\nT\nT")
            self.assertEquals(expected, result)
            self.assertFalse(collision)

    def test_conflict(self):
        common = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'

        for line in common.splitlines():
            source = common.replace(line, line + '*')
            target = common.replace(line, line + 'X')
            result, collision = three_way_merge_text(common, source, target)
            conflict = '''<<<<<<<<<<<<<<<<<<<<<<<<< base
%s*

=========================
%sX

>>>>>>>>>>>>>>>>>>>>>>>>> other''' % (line, line)
            conflicted = common.replace(line, conflict)
            self.assertEquals(conflicted, result)
            self.assertTrue(collision)

    def test_add_multiline_no_ancestor(self):
        common = None
        new = '1\n2\n3\n4\n5\n'
        other = '1\n8\n2\n3\n4\n5\n8\n'
        result, collision = three_way_merge_text(common, new, other)
        self.assertEquals(other, result)
        self.assertFalse(collision)

    def test_conflict_one_line_no_ancestor(self):
        common = ""
        base = "hola"
        other = "adios"
        result, collision = three_way_merge_text(common, base, other)
        conflict = '''<<<<<<<<<<<<<<<<<<<<<<<<< base
hola
=========================
adios
>>>>>>>>>>>>>>>>>>>>>>>>> other
'''
        self.assertEquals(conflict, result)
        self.assertTrue(collision)

    def test_conflict_multiline_no_ancestor(self):
        common = ''
        base = 'one\ntwo2\nthree\nfour\nfive\nsix\nseven\n'
        other = 'one\ntwo3\nthree\nfour\nfive\nsix\nseven\n'
        result, collision = three_way_merge_text(common, base, other)
        # THis merge is not optimal, includes extra line
        conflict = '''<<<<<<<<<<<<<<<<<<<<<<<<< base
two2

=========================
two3

>>>>>>>>>>>>>>>>>>>>>>>>> other
'''
        expected = base.replace('two2\n', conflict)
        #print expected
        self.assertEquals(expected, result)
        self.assertTrue(collision)

    def test_conflict_same_content(self):
        common = 'one\ntwo\nthree\nfour\nfive\nsix\nseven\n'
        base = 'one\ntwo\nthree\nfour4\nfive\nsix\nseven\n'
        other = 'one\ntwo\nthree\nfour4\nfive\nsix\nseven\n'
        result, collision = three_way_merge_text(common, base, other)
        self.assertEquals(base, result)
        self.assertFalse(collision)

    def test_files_conflict(self):
        base = '''aaaaa\n\nb\n\n'''
        other = '''aaaaa\n\nc\n\n'''
        common = '''aaaaa\n\nddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd\n\n'''
        result, collision = three_way_merge_text(common, base, other)
        expected = '''aaaaa

<<<<<<<<<<<<<<<<<<<<<<<<< base
b

=========================
c

>>>>>>>>>>>>>>>>>>>>>>>>> other

'''
        self.assertEquals(expected, result)
        self.assertTrue(collision)

    def test_files_conflict2(self):
        common = '''Line1
Line2
Line3
Line4
Line5

Line6
Line7

Line8 will be deleted
Line9
Line10

Line11
Line12
'''
        base = '''Line1
Line2 base change no conflict
Line3
Line4
Line5

Line6 base conflict
Line7

Line9
Line10

Line11
Line12
Base append
'''
        other = '''Line1
Line2
Line3
Line4
Line5 other change no conflict

Line6 other conflict
Line7

Line8 will be deleted
Line9
Line10

Line11 other change no conflict
Line12
'''
        result, collision = three_way_merge_text(common, base, other)
        expected = '''Line1
Line2 base change no conflict
Line3
Line4
Line5 other change no conflict

<<<<<<<<<<<<<<<<<<<<<<<<< base
Line6 base conflict

=========================
Line6 other conflict

>>>>>>>>>>>>>>>>>>>>>>>>> other
Line7

Line9
Line10

Line11 other change no conflict
Line12
Base append
'''
        self.assertEquals(expected, result)
        self.assertTrue(collision)

    def test_files_conflict3(self):
        common = '''#if ARDUINO >= 100
    #include "Arduino.h"
#else
    #include "WProgram.h"
#endif

/*dcvsvwvsv
wf
wf

v
sf
wef*/

serial serialport('#', ';', 9600);
String msg = "";
String premsg = "";
Servo myservo;

void setup() {
        myservo.attach(9);
        serialport.init();
}
'''
        base = '''#if ARDUINO >= 100
    #include "Arduino.h"
#else
    #include "WProgram.h"
#endif

/*dcvsvwvsv
wf
wf

v
sf
wef*/

serial serialport('#', ';', 9600);
String msg = "";
String premsg = "";
Servo //myservo;

void setup() {
        myservo.attach(9);
        serialport.init();
}
'''
        other = '''#if ARDUINO >= 100
    #include "Arduino.h"
#else
    #include "WProgram.h"
#endif

/*dcvsvwvsv
wf
wf

v
sf
wef*/

serial serialport('#', ';', 9600);
String msg = "";
String //premsg = "";
Servo myservo;

void setup() {
        myservo.attach(9);
        serialport.init();
}
'''
        result, collision = three_way_merge_text(common, base, other)
        expected = '''#if ARDUINO >= 100
    #include "Arduino.h"
#else
    #include "WProgram.h"
#endif

/*dcvsvwvsv
wf
wf

v
sf
wef*/

serial serialport('#', ';', 9600);
String msg = "";
<<<<<<<<<<<<<<<<<<<<<<<<< base
String premsg = "";
Servo //myservo;

=========================
String //premsg = "";
Servo myservo;

>>>>>>>>>>>>>>>>>>>>>>>>> other

void setup() {
        myservo.attach(9);
        serialport.init();
}
'''
        self.assertEquals(expected, result)
        self.assertTrue(collision)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
