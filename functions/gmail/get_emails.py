import json
from firebase_functions import https_fn
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from gmail.gmail_auth import load_credentials
from google.oauth2.credentials import Credentials


def search_emails(filters: list[str], min_discount:int, max_discount:int, stores:list[str]):
    credentials = load_credentials()
    print('credeeee:', credentials.get_cred_info()) # TESTING
    if not credentials or not credentials.valid:
        return None, https_fn.Response(
            status=302,
            headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/index'}
        )
    print('hello') # TESTING
    service = build("gmail", "v1", credentials=credentials)
    query = filters
    if min_discount != float('-inf'):
        query += f' min_discount:{min_discount}'
    if max_discount != float('inf'):
        query += f' max_discount:{max_discount}'
    if stores:
        query += f' {" OR ".join([f"from:{store}" for store in stores])}'
    print('query:', query)  # TESTING
    try:
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get('messages', [])
        filtered_emails = []
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message['id']).execute()
            filtered_emails.append(msg)
        return filtered_emails, None
    except HttpError as error:
        return None, https_fn.Response(
            json.dumps({"message": "An error occurred.", "error": str(error)}),
            status=500,
            mimetype='application/json',
        )

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