__author__ = 'n3tn0'
__version__ = 'BETA'

import imaplib2
import os
import sys
import threading
import ConfigParser
from googlevoice import Voice
from googlevoice.util import input

# Extract information from configuration file
def readconfig():
    config = ConfigParser.ConfigParser()
    config.readfp(open('config.cfg'))

    # Get the configuration options for the IMAP server and make them globally available
    section = 'IMAP'
    global server
    server = config.get(section, 'server')
    global username
    username = config.get(section, 'username')
    global password
    password = config.get(section, 'password')
    global mailbox
    mailbox = config.get (section, 'mailbox')

# Connect to and monitor the IMAP server for new mail (the main part of the script)
'''The idea to use a threading event came from __'s IMAPPush.py.  Much of this class was written with his script as a basis.'''
class Monitor(threading.Thread):
    stopwait = threading.Event()
    killing = False

    # Initial function of the class, used to log into and prepare IMAP server and start the threading event
    def __init__(self, server, username, password, mailbox):
        self.imap = imaplib2.IMAP4_SSL(server)

        # Log into the IMAP server
        try:
            self.imap.LOGIN(username, password)
        except:
            print 'There was an error logging into the IMAP server'
            sys.exit()

        # Select the appropriate mailbox and disregard messages already there
        currentmail = []
        self.imap.SELECT(mailbox)
        typ, data = self.imap.SEARCH(None, 'ALL')
        self.currentmail = data[0].split()

        # Start the threading event
        threading.Thread.__init__(self)

    # Run when the threading event starts; loops monitor program
    def run(self):
        while not self.killing:
            self.wait()


    # Waits for the mail to arrive and invokes the action
    def wait(self):
        self.newmail = False
        self.timeout = False
        self.IDLEArgs = ''
        self.stopwait.clear()

        # Run when the server receives a response from the IDLE command
        def onidleresponse(args):
            self.IDLEArgs = args
            self.stopwait.set()

        # Send IDLE command to IMAP server with what to do when done
        self.imap.idle(timeout=1799, callback=onidleresponse)
        # Wait
        self.stopwait.wait()

        #
        if not self.killing:
            # New mail has been received or a timeout has occured
            if self.IDLEArgs[0][1][0] == ('IDLE terminated (Success)'):
                typ, data = self.imap.SEARCH(None, 'UNSEEN')
                # Check if any of the IDs are in the currentmail list (irrelevant)
                for id in data[0].split():
                    # There is new mail if it isn't in the list
                    if id not in self.currentmail:
                        self.newmail = self.newmail or True
                    # It was a timeout there is no messages at all
                    elif data[0] == '':
                        self.timeout= True
                    # It was a timeout if it was already in the list
                    else:
                        self.timeout = True
            if self.newmail:
                self.alert()

    # Tell the script that new mail has been received
    def alert(self):
        typ, data = self.imap.SEARCH(None, 'UNSEEN')
        for id in data[0].split():
            if not id in self.currentmail:
                parseraw(id)
                self.currentmail.append(id)

    # Kill the script
    def kill(self):
        self.killing = True
        self.timeout = True
        self.stopwait.set()

# Collect and parse the IMAP email
def parseraw(id):
    # Connect to the IMAP serverimap
    imap = imaplib2.IMAP4_SSL(server)
    imap.LOGIN(username, password)
    imap.SELECT(mailbox)

    typ, data = imap.fetch(id, '(RFC822)' )
    body = data[0][1]
    splitmsg = body.split('\n')
    command = splitmsg[len(splitmsg)-2]
    module = command[0:command.find(' ')].lower()
    parameters = command[command.find(' '):-1]
    path = os.path.dirname(sys.executable)

    fromline = splitmsg[len(splitmsg)-6]
    splitfrom = fromline.split('\"')
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    fromphonel = []
    for i in splitfrom[1]:
        if i in numbers:
            fromphonel.append(i)
    fromphone = ''
    fromphone = fromphone.join(fromphonel)

    finalcmd = '%s/python2 modules/%s/__main__.py %s' % (path, module, parameters)
    os.system(finalcmd)
    returnmessage(fromphone)


    imap.CLOSE()
    imap.LOGOUT()

def returnmessage(phone):
    response = open('response.txt', 'r')
    message = response.readline()
    gvoice = Voice()
    gvoice.login()
    gvoice.send_sms(phone, message)

# Compile the actions into a function
def main():
    readconfig()

    monitor = Monitor(server, username, password, mailbox)
    monitor.start()

# Run the program
main()