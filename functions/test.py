import os
import json
import requests
from google_auth_oauthlib.flow import Flow
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()

# Load client secrets from a file
CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://mail.google.com/']
REDIRECT_URI = 'http://127.0.0.1:5001/oauth2callback'
# REDIRECT_URI = 'http://0.0.0.0:3000/oauth2callback' # TESTING

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

@app.get("/")
async def index():
    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    # Get the authorization code from the request
    auth_code = request.query_params.get('code')
    # Exchange the authorization code for tokens
    flow.fetch_token(code=auth_code)
    # Get the credentials
    credentials = flow.credentials
    # Use the credentials to make an authenticated request
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {credentials.token}'})
    # Make a request to the Gmail API to verify the credentials
    response = session.get('https://www.googleapis.com/gmail/v1/users/me/profile')
    if response.status_code == 200:
        return {"message": "OAuth logic is working correctly.", "user_profile": response.json()}
    else:
        return {"message": "OAuth logic failed.", "error": response.json()}

if __name__ == '__main__':
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=3000)
    uvicorn.run(app, host="127.0.0.1", port=5001) # TESTING
