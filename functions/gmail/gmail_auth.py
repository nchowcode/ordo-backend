from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
load_dotenv()  # take environment variables
import os


client_id = os.environ.get("GOOGLE_OAUTH_CLIENTID")
client_secret = os.environ.get("GOOGLE_OAUTH_CLIENTSECRET")

def exchange_authorization_code(auth_code):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://mail.google.com/'],
        redirect_uri='http://localhost:3000'  # Same as used in the client
    )
    flow.fetch_token(code=auth_code)
    credentials = flow.credentials
    return credentials