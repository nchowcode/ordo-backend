import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Use a service account to set up credentials to use firestore
cred = credentials.Certificate('SERVICE_ACCOUNT.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# set up document to get emails
emails_ref = db.collection("emails")
docs = emails_ref.stream()

# Add emails to pending field of the document; emails in pending field are used for rerendering in the pop up
def queryEmailsForAction(data):
    email_id = data['email_id']
    db.collection("emails").document(email_id).set(data)

# Return the emails that are currently in pending
def retrievePendingEmails(data):
    email_id = data['email_id']
    email = emails_ref.where(filter=FieldFilter('email_id', '==', email_id)).limit(1).get()
    
    if email:
        pending = email[0].to_dict().get('pending')
        return pending
    else:
        print("Email ID not found.")
        return None

# Delete the Emails in the pending field as User has either confirmed or cancelled their action
def cleanUpPendingEmails(data):
    email_id = data['email_id']
    email_ref = db.collection("emails").document(email_id)
    email_ref.update({"pending": []})


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

