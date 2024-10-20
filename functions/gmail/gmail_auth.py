from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
from requests import Request
from google.oauth2.credentials import Credentials
import requests
load_dotenv()  # take environment variables
import os
import json

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://mail.google.com/']
REDIRECT_URI = 'http://127.0.0.1:5001/oauth2callback'


def save_credentials(credentials):
    """Save the credentials to a file."""
    with open('token.json', 'w') as token_file:
        token_file.write(credentials.to_json())

def load_credentials():
    """Load the credentials from a file."""
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token_file:
            return Credentials.from_authorized_user_info(json.load(token_file), SCOPES)
    return None

