import unittest
from biicode.common.edition.parsing.fortran.fortran_parser import FortranParser
from biicode.common.edition.parsing.fortran.fortran_code_ref import FItem
from nose.tools.nontrivial import nottest


main = '''
InClUdE "qweqwe/qweqwe/stuff"
INCLUDE "qweqwe/qweqwe/stuffs"
PROGRAM
  USE mod ! hamilton/math
  USE matrix
  ! bungabunga
  real :: a
  a=2.0  !macaco
  call sub1(a)
  call sub2(a)
  call sub3(a)
  end
'''

mod = '''
module mod

CONTAINS

  subroutine sub1(x)
  real :: x
  print *, x
  end subroutine sub1

  subroutine sub2(x)
  real :: x
  print *, x**2
  end subroutine sub2

  subroutine sub3(x)
  real :: x
  print *, x**3
  end subroutine sub3

END mOdUlE mod
'''

real = '''
module pretty
    implicit none
    contains

    subroutine say(x)
       real::x
       include 'hello.f90'
       include 'testuser1/hello/hello.f90'
    end
end module pretty
'''


class TestFortranParser(unittest.TestCase):

    @ nottest
    def test_parserFortranTypes(self):
        fortran = FortranParser()
        fortran.parse(main)
        obtained = [ref.name for ref in fortran.includes]
        expected = ['qweqwe/qweqwe/stuff', 'qweqwe/qweqwe/stuffs']
        self.assertEqual(expected, obtained)
        obtained = fortran.declarations
        expected = set([
                        FItem('subprogram', 'sub3', ''),
                        FItem('subprogram', 'sub1', ''),
                        FItem('subprogram', 'sub2', ''),
                        ])
        self.assertEqual(expected, obtained)
        expected_modules = set([FItem('module', 'mod', 'hamilton/math'),
                                FItem('module', 'matrix')])
        self.assertItemsEqual(expected_modules, fortran.modules)
        self.assertTrue(fortran.has_main_function())

    def test_parserFortranCode(self):
        fortran = FortranParser()
        fortran.parse(mod)
        obtained = fortran.definitions
        expected = set([FItem('subprogram', 'sub3', ''),
                        FItem('subprogram', 'sub1', ''),
                        FItem('subprogram', 'sub2', ''),
                        FItem('module', 'mod', ''),
                        ])
        self.assertEqual(expected, obtained)
        self.assertEqual(fortran.has_main_function(), False)

    def test_parserFortranVoidCode(self):
        fortran = FortranParser()
        fortran.parse(mod)
        obtained = [ref.name for ref in fortran.includes]
        obtained.extend([ref.name for ref in fortran.references])
        expected = []
        self.assertEqual(expected, obtained)
        self.assertEqual(fortran.has_main_function(), False)

    def test_find_implicit_deps(self):
        parser = FortranParser()
        parser.parse(main)

        parser_two = FortranParser()
        parser_two.parse(mod)

        self.assertTrue(parser.findImplicit(parser_two))

    def test_find_implicit_deps2(self):
        parser = FortranParser()
        parser.parse(main)
        parser_two = FortranParser()
        mod = '''
        MODULE mod

        CONTAINS

          subroutine bin_array(n,x,y,n_bin,xmin,xmax,x_bin,y_bin)

            implicit none

            y_bin = s / c

          end subroutine bin_array
        END MODULE mod
        '''
        parser_two.parse(mod)
        self.assertTrue(parser.findImplicit(parser_two))

    def test_find_includes_inside_module(self):
        parser = FortranParser()
        parser.parse(real)
        includes = [include.name for include in parser.includes]
        self.assertItemsEqual(["testuser1/hello/hello.f90", "hello.f90"], includes)

if __name__ == "__main__":
    unittest.main()