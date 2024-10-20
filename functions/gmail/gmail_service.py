from typing import List
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os 
import json
from . import gmail_auth
import base64
import re
# from groq.inference import email

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://mail.google.com/']
REDIRECT_URI = 'http://127.0.0.1:5001/oauth2callback'
# REDIRECT_URI = 'http://0.0.0.0:3000/oauth2callback' # TESTING

class Message:
    id: str
    threadId: str

def get_all_messages() -> List[Message]:
    credentials = gmail_auth.load_credentials()
    service = build('gmail', 'v1', credentials=credentials) #wait for git push
    results = service.users().messages().list(userId="me",maxResults=1).execute()
    print(results)

    return results
    
    # messages.extend(response.get('messages', []))


  # Now you have a list of message IDs in 'messages'
  # Iterate through them and call users.messages.get to retrieve full details
def _get_self(service) -> str:
    result = service.users().getProfile(userId="me").execute()
    print(result)
    return result['emailAddress']

def format_messages(message_id):
    # (email, current_labels)
    # get From
    # get To ("me") dont need nothing
    # Subject
    # Body (content)
    desired_headers = ['From', 'Subject']
    extracted_headers = {}
    credentials = gmail_auth.load_credentials()
    service = build('gmail', 'v1', credentials=credentials) #wait for git push
    result = service.users().messages().get(userId="me", id = message_id).execute()
    body_content = result["payload"]["parts"][0]["body"]["data"]
    decoded_body = base64.urlsafe_b64decode(body_content).decode('utf-8')
    clean_body = _remove_links(decoded_body).replace('\r\n', '\n').strip()
    user_id = _get_self(service)
    extracted_headers['Body'] = clean_body
    extracted_headers['To'] = user_id

    print(clean_body)
    headers = result['payload']['headers']
    for header in headers:
        if header['name'] in desired_headers:
            extracted_headers[header['name']] = header['value']
    print(extracted_headers)
    # print(headers)
    # new_label = groq_label(message_body)
    # return new_label
    # {emailid1 : sports}



# delete emails based on category
def delete_emails(credentials, categories: list[str]) -> json:

    result = {"email_id" : {me},
              "pending" : []
              }
    

    return result



def stage_emails_for_deletion(service, categories, db):
    staged_emails = []



def _remove_links(text):
    url_pattern = r'https?://[^\s]+'
    cleaned_text = re.sub(url_pattern, '', text)
    cleaned_body = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_body

def add_tags(labels : list[str],userID):
    #each label has an id
#    req = "POST https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{id}/modify"
    {
    "addLabelIds": [
        "your_label_id"
    ],
    }

def create_label(userId):
    # req = "POST https://gmail.googleapis.com/gmail/v1/users/{userId}/labels"

# try
# HTTP 400 - Invalid label name 
# occurs when user custom label collides with system label
    ...

def main():
    userId = "nathanchow456@gmail.com"
    get_all_messages

main()