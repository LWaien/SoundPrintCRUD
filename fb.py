import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import json
import fb

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://concertrec-da7fc-default-rtdb.firebaseio.com/'})
ref = db.reference()
users = ref.child('users')

def insertEmailInfo(spotify_user, email,fname,lname,maxdist,location):
    keys = searchDb('spotify_user',spotify_user)
    user_key = keys[0]
    #referencing the user we want to add data for
    user = users.child(user_key)
    
    user.update({
        'email': email,
        'fname': fname,
        'lname': lname,
        'maxdist': maxdist,
        'location': location,
        
        })

    return {'msg':'email info successfully added to the the database'},201

def createNewUser(spotify_user):
    users.push({
        'email': '',
        'spotify_user': spotify_user,
        'fname': '',
        'lname': '',
        'maxdist': '',
        'location': '',
        'last_email': '',
        'top_artists': '',
        'libdata': '',
        'invites':''
        })


def searchDb(search_key,search_value):

    # Retrieve the entire dataset
    user = users.get()

    # Filter the data locally based on the key-value pair
    if user:
        result = {
            key: value
            for key, value in user.items()
            if value.get(search_key) == search_value
        }
        key_ids = list(result.keys())
        return key_ids
    else:
        return None

#Modified version of searchDb designed to look for partial completions
def searchDbForUser(search_key,search_value):

    # Retrieve the entire dataset
    user = users.get()

    # Filter the data locally based on the key-value pair
    if user:
        result = {
            key: value
            for key, value in user.items()
            if search_value.lower() in value.get(search_key).lower() 
        }
        print("result:")
        print(result)
        key_ids = list(result.keys())
        usernames = list(result.values())
        return key_ids,usernames
    else:
        return None, None


def addSpotifyData(spotify_user,topartists,libdata,topsongs):
    #search for user in db
    print(f"Adding user data for {spotify_user}")
    keys = searchDb('spotify_user',spotify_user)

    if keys is None:
        return {'msg':'Could Not Find User'},404
    
    #returns list of ids for applicable entries
    user_key = keys[0]
    #referencing the user we want to add data for
    user = users.child(user_key)
    user.update({'libdata':libdata,'top_artists':topartists,'top_songs':topsongs})
    #print(user.get())
    return 'Library data added',201

def checkData(spotify_user):
    keys = searchDb('spotify_user',spotify_user)
    user = users.child(keys[0])

    if user.get('libdata') is None and user.get('top_artists') is None:
        #return false as in user data does not exist
        return False
    else:
        return True

def get_topartists(keys):
    user_key = keys[0]
    user = users.child(user_key)    
    artist_data = user.get('email')
    #artist data is first returned as a tuple so we're just going to reference it with index 0 and then reference 'top_artists' from the dictionary within it
    artist_data = artist_data[0]['top_artists']['items']
    return artist_data

def checkPrevListDate(keys):
    user_key = keys[0]
    user = users.child(user_key)
    try:
        prev_email = user.get('previous_list')
        prev_date = prev_email[0]['last_email']
        
        date_format = "%m-%d-%Y"
        list_date = datetime.strptime(prev_date, date_format)
        today_date = datetime.now()

        # Extract the difference in days as an integer
        time_difference = today_date - list_date 
        prev_list_counter = time_difference.days
        print(prev_list_counter)

        if prev_date == "" or prev_date is None:
            return False
        #if list is less than or equal 7 days old we allow it to be shown
        elif prev_list_counter <= 7:
            return True
        else:
            return False
    except:
        return False
    
def getpreviousEmail(keys):
    user_key = keys[0]
    user = users.child(user_key)
    try:
        prev_email = user.get('previous_list')
        prev_email = prev_email[0]['previous_list']
        return prev_email
    except:
        return None
    
def checkRecSetup(keys):
    user_key = keys[0]
    user = users.child(user_key)
    try:
        dist = user.get('maxdist')
        maxdist = dist[0]['maxdist']

        if maxdist == "" or maxdist is None:
            print("recs set up: False")
            return False
        else:
            print("recs set up: True")
            return True
    except:
        print("recs set up: False")
        return False
    

def sendInv(sender_username,recipient_id):
    sender_id = searchDb('spotify_user',sender_username)
    friend_request = {
        'id': sender_id,
        'username': sender_username
    }

    # Use a transaction to append the friend request to the 'invites' array
    def transaction(transaction_data):
        if 'invites' not in transaction_data:
            transaction_data['invites'] = []

        # Check if the friend request already exists
        for invite in transaction_data['invites']:
            if invite['id'] == sender_id:
                return None  # Request already sent

        # Append the friend request
        transaction_data['invites'].append(friend_request)
        return transaction_data

    user_ref = ref.child(recipient_id)
    
    try:
        user_ref.transaction(transaction)
        return "Friend request sent successfully."
    except db.TransactionError:
        return "Failed to send friend request."