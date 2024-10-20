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
    results = service.users().messages().list(userId="me",maxResults=10).execute()
    # print(results)

    return results
    
    # messages.extend(response.get('messages', []))


  # Now you have a list of message IDs in 'messages'
  # Iterate through them and call users.messages.get to retrieve full details
def _get_self(service) -> str:
    result = service.users().getProfile(userId="me").execute()
    print(result)
    return result['emailAddress']

"""
    extract required fields from single message
    returns an object that looks like:
        {  
            From: {email_data['From']}
            To: {email_data['To']} 
            Subject: {email_data['Subject']}
            Body: {email_data['Body']}
        }
"""
def format_message(message_id):
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
    payload = result["payload"]
    # try to get the body content. If it is a MIME message, parts will not exist
    body_content = None
    if "parts" in payload.keys():
        body_content = payload["parts"][0]["body"]["data"]
    else:
        body_content = payload["body"]["data"]
    decoded_body = base64.urlsafe_b64decode(body_content).decode('utf-8')
    clean_body = _remove_links(decoded_body).replace('\r\n', '\n').strip()
    user_id = _get_self(service)
    extracted_headers['Body'] = clean_body
    extracted_headers['To'] = user_id

    
    headers = result['payload']['headers']
    for header in headers:
        if header['name'] in desired_headers:
            extracted_headers[header['name']] = header['value']
    print(extracted_headers)
    return extracted_headers
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


def get_labels() -> List[str]:
    credentials = gmail_auth.load_credentials()
    service = build("gmail", "v1", credentials=credentials)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])
    return labels

def stage_emails_for_deletion(service, categories, db):
    staged_emails = []


"""
input:
    [    
        { emailId : int, subject: str, label: str }
        # is the same as:
        Email

    ]
    

"""
# [1,2,3,4,5]


def get_new_labels(email_list: dict, curr_label_names: List[str]) -> List[str]:
    # if label in label_map does not exist in curr_label, create new label
    # goal: find unique tags from provided label_map from ai
    #       which i know will have duplicates
    # steps:
    # use curr_label as set

    new_labels = []
    existing_labels = set(curr_label_names)
    # iterate through label_map
    for email in email_list:
    # if label not present in curr_label set, it needs to be created
        if email["label"] not in existing_labels:
            new_labels.append()
    return new_labels
    # insert label to empty list
    # loop ends

    # check if label exists in current_labels
    # if it does not exist, create label via gmailapi
    # apply new label via batchApply
    # i need list of email_ids
    # i need correlating label to apply
    # im thinking { label: [email_ids] }
    
 

def create_label(userId):


        label_body = {
            "name": label,
            "labelListVisibility": "labelShow", 
            "messageListVisibility": "show",  
            "type": "user"  
        }

        results = service.users().labels().create(userId="me",body=label_body).execute()
        messages = _find_tagged_messages(label)
    # req = "POST https://gmail.googleapis.com/gmail/v1/users/{userId}/labels"

# try
# HTTP 400 - Invalid label name 
# occurs when user custom label collides with system label
    ...
        # labels are created.
    # apply all labels to correspoding emails
    # batchApplyLabels()
#   "addLabelIds": [ # A list of label IDs to add to messages.
#     "A String",
#   ],
#   "ids": [ # The IDs of the messages to modify. There is a limit of 1000 ids per request.
#     "A String",
#   ],
#   "removeLabelIds": [ # A list of label IDs to remove from messages.
#     "A String",
#   ],

def _find_tagged_messages(label: str):
    ...

    
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

def main():
    userId = "nathanchow456@gmail.com"
    get_all_messages

main()