import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from firebase_functions import https_fn
from google.auth.transport.requests import Request
from urllib.parse import parse_qs


# app = FastAPI()

# Load client secrets from a file
CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://mail.google.com/']
# REDIRECT_URI = 'http://127.0.0.1:5001/oauth2callback'
REDIRECT_URI = 'http://127.0.0.1:5001/ordo-ai/us-central1/oauth2callback'

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

def index(request: https_fn.Request):
    # Load credentials if they exist
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            return https_fn.Response(
                status=302,
                headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/profile'}
            )
        else:
            # Generate the authorization URL
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            return https_fn.Response(
                status=302,
                headers={'Location': auth_url}
            )
    else:
        return https_fn.Response(
            status=302,
            headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/profile'}
        )

def oauth2callback(request: https_fn.Request):
    # Get the authorization code from the request
    query_params = parse_qs(request.query_string.decode('utf-8'))
    # auth_code = query_params.get('code', [None])[0]
    query_params = parse_qs(request.query_string.decode('utf-8'))
    auth_code = query_params.get('code', [None])[0]
    # auth_code = request.query_params.get('code')
    if not auth_code:
        return https_fn.Response(
            json.dumps({"message": "Missing authorization code"}),
            status=400,
            mimetype='application/json'
        )
    # Exchange the authorization code for tokens
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    try:
        # Exchange the authorization code for tokens
        flow.fetch_token(code=auth_code)
    except Exception as e:
        return https_fn.Response(
            json.dumps({"message": "Failed to fetch token", "error": str(e)}),
            status=500,
            mimetype='application/json',
        )
    # Get the credentials
    credentials = flow.credentials
    save_credentials(credentials)
    return https_fn.Response(
        status=302,
        headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/profile'}
    )

def profile(request: https_fn.Request):
    # Load credentials
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        return https_fn.Response(
            status=302,
            headers={'Location': 'http://127.0.0.1:5001/ordo-ai/us-central1/index'}
        )
    try:
        # Call the Gmail API
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
    except HttpError as error:
        return https_fn.Response(
            json.dumps({"message": "An error occurred.", "error": str(error)}),
            status=500,
            mimetype='application/json',
    )
