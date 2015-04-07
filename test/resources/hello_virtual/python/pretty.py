'''
Created on 17/07/2013

@author: drodri
'''
import hello
import sys
%INCLUDE_EXTERNAL_PRETTY%


def pretty():
    sys.stdout.write('* ')
    hello.hello()
    sys.stdout.write(' *\n')

    %CALL_EXTERNAL_PRETTY%
