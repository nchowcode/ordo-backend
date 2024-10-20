import json
import re
from typing import List, TypedDict
from firebase_functions import https_fn
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from gmail.gmail_service import format_messages
from gmail.gmail_auth import load_credentials, refresh_credentials
from google.oauth2.credentials import Credentials


class DeleteMessage(TypedDict):
    name: str
    id: str
    From: str

def extract_percentage_discounts(text):
    """Extracts all percentage values from the text."""
    # Regular expression to find numbers followed by a percent sign
    percentage_regex = r'(\d{1,3})\s*%'
    matches = re.findall(percentage_regex, text)
    percentages = [int(match) for match in matches]
    return percentages


def search_emails(filters: list[str], min_discount:int, max_discount:int, stores:list[str]) -> List[DeleteMessage]:
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        # return None, https_fn.Response(
        #     status=302,
        #     headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/index'}
        # )
        credentials = refresh_credentials(credentials)
    
    service = build("gmail", "v1", credentials=credentials)
    """
        first, get everything in the promotions category
        filter out any emails that contain a %
        extract out the discount amount using regex: 80%, 20%, 10%
        parse out the integer value of the discount
        do the min/max discount filtering 
    """
    filtered_emails = []
    filters = ' OR '.join([f"label:{filter}" for filter in filters]) if filters else ''
    filter_emails = service.users().messages().list(userId="me", q=filters).execute()
    filter_messages = filter_emails.get('messages', [])

    print('EGG')
    for message in filter_messages:
        msg = format_messages(message['id'], service)
        # print('MSG: ', msg)
        filtered_emails.append((message['id'], msg['From'], msg['Subject']))
    discounts = []
    print('EGG2')

    if min_discount != None or max_discount != None:
        all_promotions = service.users().messages().list(userId="me", maxResults=50, q="category:promotions").execute() # default maxResults is 100
        
        messages = all_promotions.get('messages', [])
        for message in messages:
            msg = format_messages(message['id'], service)
            # print('msg:', msg) # TESTING
            if '%' in msg:
                # Modify the regex to allow spaces between digits
                discount_match = re.search(r'\d\s*\d*%', msg)
                if discount_match:
                    discount = discount_match.group()
                    # Remove spaces and convert to integer
                    discount = int(discount.replace(' ', '')[:-1])
                    if min_discount <= discount <= max_discount:
                        # discounts.append(message.headers['From'])
                        # print('discount:', discount) # TESTING
                        discounts.append((message['id'], msg['From'], msg['Subject'])) # (email_uid, email_from)
    
    # search for emails from stores
    stores_emails = []
    if stores:
        all_store_emails = service.users().messages().list(userId="me", maxResults=100, q=' OR '.join([f"from:{store}" for store in stores])).execute()
        store_messages = all_store_emails.get('messages', [])
        for message in store_messages:
            msg = format_messages(message['id'], service)
            stores_emails.append((message['id'], msg['From'], msg['Subject']))

    combined_emails = []
    if filtered_emails:
        combined_emails.extend(filtered_emails)
    if discounts:
        for email in discounts:
            if email not in combined_emails:
                combined_emails.append(email)
    if stores_emails:
        for email in stores_emails:
            if email not in combined_emails:
                combined_emails.append(email)
    # combined_emails_as_lists = [list(email) for email in combined_emails]
    combined_emails_as_dicts = [
        {"name": email[2], "id": email[0], "From": email[1]} for email in combined_emails
    ]
    # print('COMBINED:', combined_emails_as_dicts)

    if not combined_emails:
        return None, "No emails found."
    return combined_emails_as_dicts, None 


def user_labels(request: https_fn.Request):
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        return https_fn.Response(
            status=302,
            headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/index'}
        )
    service = build("gmail", "v1", credentials=credentials)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])
    if not labels:
        return https_fn.Response(
            json.dumps({"message": "No labels found."}),
            status=200,
            mimetype='application/json',
        )
    return https_fn.Response(
        json.dumps({"message": "OAuth logic is working correctly.", "labels": labels}),
        status=200,
        mimetype='application/json',
    )
# except HttpError as error:
#     return https_fn.Response(
#         json.dumps({"message": "An error occurred.", "error": str(error)}),
#         status=500,
#         mimetype='application/json',
# )


def delete_emails(request: https_fn.Request):
    # Load credentials
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        return https_fn.Response(
            status=302,
            headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/index'}
        )
    try:
        # Call the Gmail API to get the user's email
        service = build("gmail", "v1", credentials=credentials)
        user_info = service.users().getProfile(userId="me").execute()
        user_email = user_info['emailAddress']

        # Perform the action to delete emails
        # For example, delete emails from the inbox
        query = 'in:inbox'
        messages = service.users().messages().list(userId="me", q=query).execute().get('messages', [])
        for message in messages:
            service.users().messages().delete(userId="me", id=message['id']).execute()

        return https_fn.Response(
            json.dumps({"message": f"Emails deleted for user {user_email}."}),
            status=200,
            mimetype='application/json',
        )
    except HttpError as error:
        return https_fn.Response(
            json.dumps({"message": "An error occurred.", "error": str(error)}),
            status=500,
            mimetype='application/json',
    )