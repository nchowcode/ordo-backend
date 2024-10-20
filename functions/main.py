# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

# from functions_framework import http, https_fn
import json
from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore
# from entry_point import app
from firebase_admin import firestore 
import gmail.gmail_auth as gmailAuth
import gmail.gmail_service as gmailService
import database.firestore as gmailDatabase

initialize_app()
db = firestore.client()

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

@https_fn.on_request()
def deleteEmails(request: https_fn.Request):
    if request.method == 'POST':
        deleteMusic = gmailDatabase.filterEmails(request, db)
        email = request.get_json()['email']
        gmailDatabase.deleteEmails(email, deleteMusic, db)
    return https_fn.Response(
        json.dumps({"message": "Only POST requests are allowed."}),
        status=405,
        mimetype='application/json',
    )
    # return gmailDatabase.deleteEmails(request, db)

@https_fn.on_request()
def filters(request: https_fn.Request):
    return gmailService.get_labels()


@https_fn.on_request()
def stores(request: https_fn.Request):
    return gmailService.get_stores(request)

@https_fn.on_request()
def queryEmailsForAction(request: https_fn.Request):
    return gmailDatabase.queryEmailsForAction(request, db)

@https_fn.on_request()
def retrievePendingEmails(request: https_fn.Request):
    return gmailDatabase.retrievePendingEmails(request, db)

@https_fn.on_request()
def cleanUpPendingEmails(request: https_fn.Request):
    return gmailDatabase.cleanUpPendingEmails(request, db)