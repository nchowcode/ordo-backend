import json
from typing import List
from urllib.parse import parse_qs
import firebase_admin
from firebase_admin import firestore, initialize_app
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_functions import https_fn
import json

from gmail.gmail_auth import load_credentials, refresh_credentials
from gmail.get_emails import DeleteMessage, search_emails

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


# JSON object:
# {
#   filters: [] : string,
#   discount: [] : int ,
#   stores: [] : string,
# }

# GET MAX 20 EMAILS   

# what i need back:
# JSON object:
# {
#   deletedEmails: [] : {object that has "name" as a variable so I can use it to display name of email}
# } 
def filterEmails(request: https_fn.Request, db: firestore.Client):
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Request data is missing.")
        filters = data.get('filters', None)
        discounts = data.get('discount', None)
        min_discount = discounts[0] if discounts and discounts[0] else None
        max_discount = discounts[1] if discounts and discounts[1] else None
        # min_discount, max_discount = data.get('discount', (None, None))
        stores = data.get('stores', None)
        if min_discount is None and max_discount is None:
            min_discount = None
            max_discount = None
        else:
            min_discount = 0 if min_discount is None else int(min_discount)
            max_discount = 100 if max_discount is None else int(max_discount)
        # print('tttt:', filters, discounts, stores) # TESTING
        filtered_emails, err = search_emails(filters, min_discount, max_discount, stores)
        # if filtered_emails: #TESTING
        #     print('there is filters:', filtered_emails)  # TESTING
        if err:
            print(f"An error occurred while searching for emails: {err}")
            raise Exception("An error occurred while searching for emails.")
        # return https_fn.Response(
        #     json.dumps({"deletedEmails": filtered_emails}),
        #     status=200,
        #     mimetype='application/json',
        # )
        return filtered_emails
    except ValueError as ve:
        return https_fn.Response(
            json.dumps({"message": "invalid argument", "error": str(ve)}),
            status=500,
            mimetype='application/json',
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        return https_fn.Response(
            json.dumps({"message": "An error occurred.", "error": str(e)}),
            status=500,
            mimetype='application/json',
        )

    # emails_ref = db.collection("emails")
    # docs = emails_ref.stream()

    # deleted_emails = []
    # for doc in docs:
    #     email = doc.to_dict()
    #     if email['store'] in stores and email['discount'] in discount and email['filter'] in filters:
    #         deleted_emails.append(email)
    #         doc.delete()

    # return

def deleteEmails(email_id: str, deletedMusic: List[DeleteMessage], db: firestore.client):
    # credentials = load_credentials()
    # if not credentials or not credentials.valid:
    #     credentials = refresh_credentials()
    # print(credentials.get_cred_info())
    print(email_id)

    # email_id = credentials.id_token['email']
    # print('deleteemail email_id:', email_id) #TESTING
    # email_id = deletedMusic['email_id']
    # email_ref = db.collection("emails").document(email_id)
    # email_ref.delete()


def testFunctions():
    test_data = {
        'email_id' : 'test@gmail.com'
    }

    test_data2 =  {
    'email_id': 'something@gmail.com',
    'pending': ['email7', 'email3', 'email9']
    }

    pending = retrievePendingEmails(test_data)
    print(pending)

    queryEmailsForAction(test_data2)

    cleanUpPendingEmails(test_data)
