import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_functions import https_fn

from gmail.get_emails import search_emails

# # Use a service account to set up credentials to use firestore
# cred = credentials.Certificate('SERVICE_ACCOUNT.json')
# app = firebase_admin.initialize_app(cred)
# db = firestore.client()

# # set up document to get emails
# emails_ref = db.collection("emails")
# docs = emails_ref.stream()

# Add emails to pending field of the document; emails in pending field are used for rerendering in the pop up
def queryEmailsForAction(data, db: firestore.client):
    email_id = data['email_id']
    db.collection("emails").document(email_id).set(data)

# Return the emails that are currently in pending
def retrievePendingEmails(data, db: firestore.client):
    email_id = data['email_id']
    emails_ref = db.collection("emails")
    email = emails_ref.where(filter=FieldFilter('email_id', '==', email_id)).limit(1).get()
    
    if email:
        pending = email[0].to_dict().get('pending')
        return pending
    else:
        print("Email ID not found.")
        return None

# Delete the Emails in the pending field as User has either confirmed or cancelled their action
def cleanUpPendingEmails(data, db: firestore.client):
    email_id = data['email_id']
    email_ref = db.collection("emails").document(email_id)
    email_ref.update({"pending": []})


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

