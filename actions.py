import base64
from db import get_database_connection

import email

import httplib2
import json

import os
from oauth2client import tools


def MessagesWithMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
          page_token = response['nextPageToken']
          response = service.users().messages().list(userId=user_id, q=query,
                                             pageToken=page_token).execute()
          messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

def MessagesWithLabels(service, user_id, label_ids=[]):
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

    Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
    
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
          messages.extend(response['messages'])

        while 'nextPageToken' in response:
          page_token = response['nextPageToken']
          response = service.users().messages().list(userId=user_id,
                                                     labelIds=label_ids,
                                                     pageToken=page_token).execute()
          messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

def get_mpart(mail):
    maintype = mail.get_content_maintype()
    if maintype == 'multipart':
        for part in mail.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
        return ""
    elif maintype == 'text':
        return mail.get_payload()

def get_mail_body(mail):
    """
    There is no 'body' tag in mail, so separate function.
    :param mail: Message object
    :return: Body content
    """
    body = ""
    if mail.is_multipart():
        body = get_mpart(mail)
    else:
        body = mail.get_payload()
    return body

def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

    Returns:
    A Message.
    
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_string(msg_str)
        data = {}
        data['to'] = mime_msg['To']
        data['from'] = mime_msg['From']
        data['date'] = mime_msg['Date']
        data['subject'] = mime_msg['Subject']
        data['message'] = ""
        return data
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

def get_all_labels(service,user_id):
    results = service.users().labels().list(userId=user_id).execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])


def fetch_and_store_in_db(service,user_id):
    conn = get_database_connection()
    cur = conn.cursor()
    messages = MessagesWithLabels(service, user_id, ['INBOX'])
    for msg in messages:
        result = GetMessage(service, user_id, msg['id'])
        result['date'] = " ".join(result['date'].split()[:5])
        conv = time.strptime(result['date'], "%a, %d %b %Y %H:%M:%S")
        result['date'] = time.strftime("%Y-%m-%d %H:%M:%S", conv)
        result['msg_id'] = msg['id']
        # Insert data into tables. 
        cur.execute(
            "INSERT INTO mail_data(email_from,email_to,email_subject,email_message,email_received,message_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (result['from'], result['to'], result['subject'], result['message'], result['date'],str(result['msg_id'])))
        conn.commit()
    conn.close()

def execute_rules():
    conn = get_database_connection()
    cur = conn.cursor()
    rules = json.load(open('rules.json'))
    for rule in rules["1"]["criteria"]:
        query = "SELECT message_id FROM mail_data WHERE " + "email_" + rule["name"] + " LIKE '"+rule["value"][1]+"'"
        cur.execute(query)
        print(cur.fetchall())