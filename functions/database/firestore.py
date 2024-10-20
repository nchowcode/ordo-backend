import json
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
        data = request.json
        print('data:', data)  # TESTING
        # Validate input data
        if not data:
            raise ValueError("Request data is missing.")
        if 'filters' not in data or 'stores' not in data:
            raise ValueError("Required fields 'filters' and 'stores' are missing.")
        filters = data['filters']
        min_discount, max_discount = data.get('discount', (0, 100))
        stores = data['stores']
        # Convert discounts to integers, handling special cases
        min_discount = 0 if min_discount == 0 else int(min_discount)
        max_discount = 100 if max_discount == 100 else int(max_discount)
        # Search for emails
        filtered_emails, err = search_emails(filters, min_discount, max_discount, stores)
        print('filtered_emails:', filtered_emails)  # TESTING
        if err:
            raise Exception("An error occurred while searching for emails.")
        print('filtered_emails:', filtered_emails)  # TESTING
        return https_fn.Response(
            json.dumps({"filtered_emails": filtered_emails}),
            status=200,
            mimetype='application/json',
        )
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

# def deleteEmails(data, db: firestore.client):
#     email_id = data['email_id']
#     email_ref = db.collection("emails").document(email_id)
#     email_ref.delete()


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
