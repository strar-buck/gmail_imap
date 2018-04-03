from __future__ import print_function

from apiclient import discovery
from auth import get_credentials
from actions import (
    get_all_labels,
    fetch_and_store_in_db,
    execute_rules,
)

import httplib2


def main():
    """Shows basic usage of the Gmail API.

        Creates a Gmail API service object and outputs a list of label names
        of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    user_id = 'me'

    get_all_labels(service,user_id)
    fetch_and_store_in_db(service,user_id)
    
    execute_rules()


main()