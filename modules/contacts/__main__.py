#!/usr/bin/env python2

__author__ = 'n3tn0'
__version__ = 'ALPHA'

import ConfigParser
import sys
import os

#os.chdir('modules/' + sys.argv[0])
os.chdir(sys.argv[0][:-11])
response = open('../../response.txt', 'w')

# Define special words that are not names but are special commands
special = ['addnew', 'autoparse']

# Get contact info from config file
def getcontactinfo(name, detail):
    contacts = ConfigParser.ConfigParser()
    contacts.readfp(open('contacts.cfg'))

    try:
        lookup = contacts.get(name.title(), detail)
    except:
        lookup = contacts.get(name, detail)

    return lookup

if sys.argv[1] not in special:
    lookup = getcontactinfo(sys.argv[1], sys.argv[2])
    if sys.argv[2].find('phone'):
        sys.argv[2] = sys.argv[2] + ' number'
    final = '%s\'s %s is %s.' % (sys.argv[1].title(), sys.argv[2], lookup)
    response.write(final)
elif sys.argv[1] == 'autoparse':
    for i in os.listdir('./parse'):
        os.system('python parse.py %s' % i)
    with open('response.txt', 'w') as f:
        response.write(f.readline())


response.close()
