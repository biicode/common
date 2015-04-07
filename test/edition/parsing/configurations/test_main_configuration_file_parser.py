from biicode.common.edition.parsing.conf.main_conf_file_parser import (EntryPointConfiguration,
                                                                       parse_mains_conf)
from biicode.common.test.bii_test_case import BiiTestCase


class TestEntryPointConfigurationFileParser(BiiTestCase):
    def test_simple_file(self):
        text = 'main.h'
        mains = parse_mains_conf(text, "mains.bii")
        expected = [EntryPointConfiguration.parse("main.h")]
        self.assert_bii_equal(expected, mains)

    def test_dynlib_def(self):
        text = r'''block.h DYNLIB
        main.cpp'''
        mains = parse_mains_conf(text, "mains.bii")
        expected = [EntryPointConfiguration.parse("block.h DYNLIB"),
                    EntryPointConfiguration.parse("main.cpp")]
        self.assert_bii_equal(expected, mains)

    def test_non_main(self):
        text = '!main.cpp'
        mains = parse_mains_conf(text, "mains.bii")
        expected = [EntryPointConfiguration.parse("!main.cpp")]
        self.assert_bii_equal(expected, mains)
        for main in mains:
            self.assertFalse(main.has_main)

    def test_multiple_lines(self):
        text = r'''main.cpp
        hello.h
        !test.cpp'''
        mains = parse_mains_conf(text, "mains.bii")
        expected = [EntryPointConfiguration.parse("main.cpp"),
                    EntryPointConfiguration.parse("hello.h"),
                    EntryPointConfiguration.parse("!test.cpp")]
        self.assert_bii_equal(expected, mains)
