# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

# from functions_framework import http, https_fn
from firebase_functions import https_fn
from firebase_admin import initialize_app
# from entry_point import app
import gmail.gmail_auth as gmailAuth

initialize_app()

# @http
# def fastapi_app(request):
#     return app(request.scope, request.receive, request.send)


@https_fn.on_request()
def index(request: https_fn.Request):
    return gmailAuth.index(request)

@https_fn.on_request()
def oauth2callback(request: https_fn.Request):
    return gmailAuth.oauth2callback(request)

@https_fn.on_request()
def profile(request: https_fn.Request):
    return gmailAuth.profile(request)
