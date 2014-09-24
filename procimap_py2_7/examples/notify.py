#!/usr/bin/env python
"""
    Notify of new mail. Notify immediately for people in my notify list. Notify
    immediately with special sound for people in my priority list. For everyone
    else, notify if the email has been sitting on the server unread for more
    than an hour. However, once notification happens, it will be for all unread
    messages on the server.
"""

from ProcImap.Utils.MailboxFactory import MailboxFactory
from time import time
import sys
import os
import cPickle
import re
import email


try:
    inbox = MailboxFactory("mailboxes.cfg")['GVoice']
    #prioritylist = AddressListFile("/Users/goerz/.procimap/priority.lst")
    #notifylist = AddressListFile("/Users/goerz/.procimap/notify.lst")
    picklefile = "notify.pickle"
    imageslist = "pictures.txt"

    notifytimeout = 3600

    unread_mails = {}

    unseen = inbox.get_unseen_uids()
except:
    sys.exit(0)



def get_icon(address):
    images_fh = open(imageslist)
    for line in images_fh:
        print line
        (imgadress, icon) = line.split()
        if imgadress in address:
            return icon
    images_fh.close()
    return "/Users/goerz/Library/Images/GmailIcon.png"

def get_address(rawaddress):
    addresspattern = re.compile(r'(.*) (<.*>)')
    addressmatch = addresspattern.search(rawaddress)
    if addressmatch:
        return addressmatch.group(1)
    else:
        return rawaddress



def notify(priority=False):
    for uid in unread_mails.keys():
        if unread_mails[uid][4] is False:
            output = open('output.txt', 'r+')
            output.write('"')
            decoded_subject = u""
            for part in email.header.decode_header(unread_mails[uid][2]):
                if part[1] is None:
                    decoded_subject += unicode(part[0])
                else:
                    decoded_subject += part[0].decode(part[1])
            output.write(decoded_subject.encode('utf-8'))
            output.write('"')
            (code, data) = inbox._server.uid('fetch', uid, '(BODY.PEEK[1])')
            if code == 'OK':
                output.write("\n")
                body = data[0][1][:60]
                body = body.decode(unread_mails[uid][3])
                body = body.replace("\r\n", " ")
                body = body.replace("\n", " ")
                body = body.replace("\r", " ")
                body = body.replace("\t", " ")
                body = body.replace("  ", " ")
                output.write(body.encode('utf-8'))
                output.write("...")
            output.write("command")
            output.close()
            unread_mails[uid][4] = True # mark as notified


# unpickle data from disk
if os.path.isfile(picklefile):
    input = open(picklefile, 'rb')
    unread_mails = cPickle.load(input)
    input.close()

# clean up
for uid in unread_mails.keys():
    if not uid in unseen:
        del(unread_mails[uid])

# notify as necessary
if len(unseen) > 0:
    for uid in unseen:
        if unread_mails.has_key(uid):
            if (int(time()) - unread_mails[uid][0]) < notifytimeout:
                notify()
        else:
            fields = inbox.get_fields(uid, "From Subject Content-Type")
            from_address = fields['From']
            subject = fields['Subject']
            encoding = fields.get_content_charset()
            if not isinstance(encoding, str):
                encoding = 'ascii'
            #if prioritylist.contains(from_address):
            if from_address == 'timothy.noto4@gmail.com': #####
                notify()
                unread_mails[uid] = [int(time()), from_address, subject,
                                     encoding, False]
                notify(priority=True)
            #elif notifylist.contains(from_address):
            elif from_address == 'cowshower248@gmail.com': #####
                unread_mails[uid] = [int(time()), from_address, subject,
                                     encoding, False]
                notify()
            else:
                unread_mails[uid] = [int(time()), from_address, subject,
                                     encoding, False]


    # pickle data to disk
    output = open(picklefile, 'wb')
    cPickle.dump(unread_mails, output, protocol=2)
    output.close()



print "End"
inbox.close()
#sys.exit(0)
