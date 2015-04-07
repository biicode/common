'''
Created on 17/07/2013

@author: drodri
'''
import sys, os


def hello():
    #bii://data.bmp
    #bii://data.xml
    file_path = os.path.join(os.path.dirname(__file__), "data/data.bmp")
    with open(file_path, 'r') as fin:
        content = fin.read()
        sys.stdout.write(content.rstrip())
    file_path = os.path.join(os.path.dirname(__file__), "data/data.xml")
    with open(file_path, 'r') as fin:
        content = fin.read()
        sys.stdout.write(content.rstrip())
