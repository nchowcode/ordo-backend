import os
import json
from google.oauth2.credentials import Credentials
import requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from gmail import gmail_service, gmail_auth
from groqllm.inference import assign_label
# from gmail.gmail_auth import load_credentials, save_credentials
 

app = FastAPI()

# Load client secrets from a file
CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://mail.google.com/']
REDIRECT_URI = 'http://127.0.0.1:5001/oauth2callback'
# REDIRECT_URI = 'http://0.0.0.0:3000/oauth2callback' # TESTING

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

@app.get("/")
async def index():
    # Load credentials if they exist
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # Generate the authorization URL
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            return RedirectResponse(auth_url)
    else:
        return RedirectResponse(url='/profile')

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    # Get the authorization code from the request
    auth_code = request.query_params.get('code')
    # Exchange the authorization code for tokens
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    # Exchange the authorization code for tokens
    flow.fetch_token(code=auth_code)
    # Get the credentials
    credentials = flow.credentials
    save_credentials(credentials)
    return RedirectResponse(url='/profile')

@app.get("/profile")
async def profile():
    # Load credentials
    credentials = load_credentials()
    if not credentials or not credentials.valid:
        return RedirectResponse(url='/')
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=credentials)
        results = service.users().labels().list(userId="me").execute()
        test()
        labels = results.get("labels", [])
        
        if not labels:
            print("No labels found.")
            return
        print("Labels:")
        for label in labels:
            print(label["name"])
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

@app.get("/test")
async def test():
    result = gmail_service.get_all_messages()
    label_map = {}
    list_obj = result["messages"]
    curr_labels_obj = gmail_service.get_labels()
    label_names = [label["name"] for label in curr_labels_obj]
    print("labels", label_names)
    for email in list_obj:
        email_obj = gmail_service.format_messages(email["id"])
        label = assign_label(email_obj, label_names) #jose func
        label_map[email_obj["Subject"]] = label
    gmail_service.apply_label(label_map,label_names)
    print(label_map)
    # go through each email in results
    # extract content from id 
    # add each content line to a list
    # convert content to class email 
    # put it in a list to sent to ai 
    # --- jose's code will take in the returned obj
    # ai would return list categories / labels 
    # ---- my code takes list of labels 
    # retreive current labels with function 
    # retreive list of labels from ai
    # eliminate duplicates from overlapping labels with set
    # list of new labels 
    # create new labels, labels.color
    # apply labels to corresponding email ids
    
    # hm = {}
    # for _ in range(10):
    #     label = format_messages(message_id)
    #     hm[message_id] = label
    # return hm 
        

    # # Use the credentials to make an authenticated request
    # session = requests.Session()
    # session.headers.update({'Authorization': f'Bearer {credentials.token}'})
    # # Make a request to the Gmail API to verify the credentials
    # response = session.get('https://www.googleapis.com/gmail/v1/users/me/profile')
    # if response.status_code == 200:
    #     return {"message": "OAuth logic is working correctly.", "user_profile": response.json()}
    # else:
    #     return {"message": "OAuth logic failed.", "error": response.json()}


    # # Use the credentials to make an authenticated request
    # session = requests.Session()
    # session.headers.update({'Authorization': f'Bearer {credentials.token}'})
    # # Make a request to the Gmail API to verify the credentials
    # response = session.get('https://www.googleapis.com/gmail/v1/users/me/profile')
    # if response.status_code == 200:
    #     return {"message": "OAuth logic is working correctly.", "user_profile": response.json()}
    # else:
    #     return {"message": "OAuth logic failed.", "error": response.json()}
    


# example output:
# {
#   "message": "OAuth logic is working correctly.",
#   "user_profile": {
#     "emailAddress": "josegonz115@gmail.com",
#     "messagesTotal": 15513,
#     "threadsTotal": 14859,
#     "historyId": "1941707"
#   }
# }

if __name__ == '__main__':
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=3000)
    uvicorn.run(app, host="127.0.0.1", port=5001) # TESTING
