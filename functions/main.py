# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from functions_framework import http
from firebase_admin import initialize_app

from entry_point import app

initialize_app()


@http
def fastapi_app(request):
    return app(request.scope, request.receive, request.send)

