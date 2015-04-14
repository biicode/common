'''
Created on 17/07/2013

@author: drodri
'''
import pretty
import sys

if __name__ == '__main__':
    # For test input parameters
    if len(sys.argv) > 0:
        for arg in sys.argv:
            print arg

    pretty.pretty()
