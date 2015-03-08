__author__ = 'n3tn0'
__version__ = 'ALPHA'

import os
import sys

# os.chdir('modules/' + sys.argv[0])
os.chdir(sys.argv[0][:-9]+'/parse')

global cardname
cardname = sys.argv[1]


def putinlist():
    vcard = open(cardname, 'r')
    text = []

    for i, l in enumerate(vcard):
        pass
    lines = i + 1
    vcard.close()

    vcard2 = open(cardname, 'r')
    for i in range(0, lines):
        text.append(vcard2.readline()[:-2])
    vcard2.close()
    return text


def extractname(text):
    nameline = text[1]
    start = nameline.find(';') + 1
    name = nameline[start:-3]
    return name


def getemails(text):
    email = 0
    emails = {}

    for i in text:
        if not i.find('EMAIL'):
            start = i.find(':') + 1
            if not email:
                emails['email'] = i[start:]
            else:
                emails['email'+str(email+1)] = i[start:]
            email += 1

    return emails


def gettels(text):
    tels = {}

    for i in text:
        if not i.find('TEL'):
            typestart = i.find(';')
            numberstart = i.find(':')
            teltype = i[typestart+1:numberstart]
            number = i[numberstart+1:]
            tels[teltype] = number

    return tels


def writeit(name, tels, emails):
    contacts = open('../contacts.cfg', 'a')

    contacts.write('\n\n[%s]\n' % name)

    for i in tels:
        contacts.write('%sphone = %s\n' % (i.lower(), tels[i]))

    for i in emails:
        contacts.write('%s = %s\n' % (i.lower(), emails[i]))


def writeresponse(name):
    response = open('../response.txt', 'w')
    response.write('vCard import successful.  %s has been added to your contacts.' % name)
    response.close()

def main():
    text = putinlist()

    name = extractname(text)
    emails = getemails(text)
    tels = gettels(text)

    writeit(name, tels, emails)

    writeresponse(name)

    os.delete(cardname)
    os.delete('../response.txt')


main()
