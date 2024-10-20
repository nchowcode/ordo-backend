from urllib.parse import parse_qs
import firebase_admin
from firebase_admin import firestore 
from firebase_admin import initialize_app
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_functions import https_fn
import json

# Add emails to pending field of the document; emails in pending field are used for rerendering in the pop up
def queryEmailsForAction(request: https_fn.Request, db: firestore.client):
    try:
        if request.method != 'POST':
            return https_fn.Response(
                json.dumps({"message": "Only POST requests are allowed."}),
                status=405,
                mimetype='application/json',
            )
        
        data = request.get_json()
        email_id = data.get('email_id')
        pending_emails = data.get('pending')  

        if not email_id or not pending_emails:
            return https_fn.Response(
                json.dumps({"message": "email_id and emails are required."}),
                status=400, 
                mimetype='application/json',
            )
        
        email_doc_ref = db.collection("emails").document(email_id)

        # Add emails to the pending field
        email_doc_ref.set({
            'pending': firestore.ArrayUnion(pending_emails)  # Add emails to the pending field
        })

        return https_fn.Response(
            json.dumps({"message": "Emails successfully added to pending."}),
            status=200,
            mimetype='application/json',
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"message": "Failed to add emails to pending", "error": str(e)}),
            status=500,
            mimetype='application/json',
        )

# Return the emails that are currently in pending
def retrievePendingEmails(request: https_fn.Request, db: firestore.client):
    query_params = parse_qs(request.query_string.decode('utf-8'))
    email_id = query_params.get('email_id', [None])[0]
    emails_ref = db.collection("emails")
    
    try:
        email = emails_ref.where(filter=FieldFilter('email_id', '==', email_id)).limit(1).get()
        if email:
            pending = email[0].to_dict().get('pending')
            return https_fn.Response(
                json.dumps({"message": "Successfully retrieved pending emails", "pending_emails": pending}),
                status=200,
                mimetype='application/json',
            )
        else:
            return https_fn.Response(
                json.dumps({"message": "Failed to find email address", "error": str(e)}),
                status=500,
                mimetype='application/json',
            )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"message": "Failed to retrieve pending emails", "error": str(e)}),
            status=500,
            mimetype='application/json',
        )


# Delete the Emails in the pending field as User has either confirmed or cancelled their action
def cleanUpPendingEmails(request: https_fn.Request, db: firestore.client):
    query_params = parse_qs(request.query_string.decode('utf-8'))
    email_id = query_params.get('email_id', [None])[0]
    try:
        email_ref = db.collection("emails").document(email_id)
        email_ref.update({"pending": []})
        return https_fn.Response(
            json.dumps({"message": "Successfully cleared emails in pending field."}),
            status=200,
            mimetype='application/json',
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"message": "Failed to add delete pending emails", "error": str(e)}),
            status=500,
            mimetype='application/json',
        )

