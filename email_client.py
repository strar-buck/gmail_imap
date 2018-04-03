import datetime

import email
import email.header

import getpass

import imaplib

import sys


def processing_mailbox(conn):

    res, data = conn.search(None, "ALL")
    if res != 'OK':
        return

    for num in data[0].split():
        res, data = conn.fetch(num, '(RFC822)')
        if res != 'OK':
            return

        msg = email.message_from_string(data[0][1])
        decode = email.header.decode_header(msg['Subject'])[0]
        subject = decode[0]
        print('Message %s: %s' % (num, subject))

        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))



def get_gmail_imap_connection():
    conn = imaplib.IMAP4_SSL('imap.gmail.com')

    try:
        res, data = conn.login(USERNAME, PASSWORD)
    except imaplib.IMAP4.error:
        print("Authentication Failed")
        sys.exit(1)

    res, mails = conn.list()
    if res == 'OK':
        for i in mails:
            print(i.decode("utf-8"))

    res, data = conn.select(mailbox="INBOX")
    if res == 'OK':
        print("Processing mailbox...\n")
        processing_mailbox(conn)
        conn.close()
    else:
        print("Unable to open mailbox ", res)

    conn.logout()

get_gmail_imap_connection()

