'''
Created on 17/07/2013

@author: drodri
'''
import hello
import sys
%INCLUDE_EXTERNAL_PRETTY%


def pretty():
    print '*',
    hello.hello()
    print '*'

    %CALL_EXTERNAL_PRETTY%
