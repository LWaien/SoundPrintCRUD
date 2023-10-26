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
    try:
        sender_id = searchDb('spotify_user',sender_username)
    except:
        return "Failed to send friend request",404
    
    friend_request = {
        'id': sender_id[0],
        'username': sender_username
    }

    # Use a transaction to append the friend request to the 'invites' array
    def transaction(transaction_data):

        if transaction_data is None:
            transaction_data = {}

        if 'invites' not in transaction_data:
            transaction_data['invites'] = []

        duplicateFlag = False
        for invite in transaction_data['invites']:
            #print(invite['username'])
            if invite['username'] == sender_username:
                 duplicateFlag = True
                 #print(duplicateFlag) # Request already sent

        if duplicateFlag is False:
            transaction_data['invites'].append(friend_request)
        return transaction_data

    user_ref = users.child(recipient_id)
    
    try:
        user_ref.transaction(transaction)
        return "Friend request sent successfully",200
    except:
        return "Failed to send friend request",404
    
def getInvites(spotify_user):
    ids = searchDb('spotify_user',spotify_user)
    user = users.child(ids[0])
    try:
        invite_list = user.get('invites')
        invites = invite_list[0]['invites']
        return invites
    except:
        return None
    
def acceptInvite(friend_user, friend_id, spotify_user):
    try:
        user_id = searchDb('spotify_user', spotify_user)
    except:
        return "Failed to accept friend request", 404

    friend_data = {
        'id': friend_id,
        'username': friend_user
    }

    # Use a transaction to append the friend request to the 'friends' array of the accepting user
    def transaction(transaction_data):
        if transaction_data is None:
            transaction_data = {}

        if 'friends' not in transaction_data:
            transaction_data['friends'] = []

        if 'invites' not in transaction_data:
            transaction_data['invites'] = []

        duplicateFlag = False

        for friend in transaction_data['friends']:
            if friend['username'] == friend_user:
                duplicateFlag = True

        if not duplicateFlag:
            transaction_data['friends'].append(friend_data)

            # Remove friend from invites list now that we added to friends
            for invite in transaction_data['invites']:
                if invite['username'] == friend_user:
                    transaction_data['invites'].remove(invite)

        return transaction_data

    user_ref = users.child(user_id[0])
    user_ref2 = users.child(friend_id)

    try:
        user_ref.transaction(transaction)
        user_ref2.transaction(transaction)

        # Remove the friend request from the inviting user's sent invites list
        removePending(friend_user, user_id[0])


        return "Friend request accepted, and friends added", 200
    except:
        return "Failed to accept friend request", 404


def getFriends(spotify_user):

    user_id = searchDb('spotify_user', spotify_user)
 
    
    user = users.child(user_id[0])


    friends_list = user.get('friends')
    friends = friends_list[0]['friends']
    return friends


def addPending(spotify_user, recipient_id):
    # Get the sender's data by their Spotify username
    sender_ids = searchDb('spotify_user', spotify_user)

    if sender_ids:
        sender_id = sender_ids[0]
        sender_ref = users.child(sender_id)

        # Retrieve the existing sent invites
        sender_data = sender_ref.get()
        sent_invites = sender_data.get('sent_invites', [])

        # Check for duplicate invites and avoid adding duplicates
        duplicate_invite = any(invite['id'] == recipient_id for invite in sent_invites)

        if not duplicate_invite:
            # Add the new invite to the sent_invites list
            recipientuser = users.child(recipient_id)
            recipientusername = recipientuser.get('spotify_user')
            recipientusername = recipientusername[0]['spotify_user']
            new_invite = {'id': recipient_id,'recipient_username':recipientusername}
            sent_invites.append(new_invite)

            # Update the sender's data with the new sent_invites list
            sender_ref.update({'sent_invites': sent_invites})

            return {'msg': f'Sent friend request to {recipient_id} added to sent_invites'}, 200
        else:
            return {'msg': 'Friend request already sent to this user'}, 400
    else:
        return {'msg': 'Sender not found'}, 404

def getPending(spotify_user):

    user_id = searchDb('spotify_user', spotify_user)
 
    
    user = users.child(user_id[0])


    sent_invites = user.get('sent_invites')
    pendingList = sent_invites[0]['sent_invites']
    return pendingList

def removePending(sender_spotify_user, recipient_id):
    # Get the sender's data by their Spotify username
    sender_ids = searchDb('spotify_user', sender_spotify_user)

    if sender_ids:
        sender_id = sender_ids[0]
        sender_ref = users.child(sender_id)

        # Retrieve the existing sent invites
        sender_data = sender_ref.get()
        sent_invites = sender_data.get('sent_invites', [])

        # Check if the recipient_id exists in the sent_invites list
        found_invite = next((invite for invite in sent_invites if invite['id'] == recipient_id), None)

        if found_invite:
            # Remove the invite from the sent_invites list
            sent_invites.remove(found_invite)

            # Update the sender's data with the updated sent_invites list
            sender_ref.update({'sent_invites': sent_invites})

            return {'msg': f'Friend request to {recipient_id} removed from sent_invites'}, 200
        else:
            return {'msg': 'Friend request not found in the sent_invites list'}, 404
    else:
        return {'msg': 'Sender not found'}, 404



def removeInvite(sender_spotify_user, recipient_id):
    # Get the sender's data by their Spotify username
    sender_ids = searchDb('spotify_user', sender_spotify_user)

    if sender_ids:
        sender_id = sender_ids[0]
        sender_ref = users.child(sender_id)

        # Retrieve the existing invites
        sender_data = sender_ref.get()
        invites = sender_data.get('invites', [])

        # Check if the recipient_id exists in the invites list
        found_invite = next((invite for invite in invites if invite['id'] == recipient_id), None)

        if found_invite:
            # Remove the invite from the invites list
            invites.remove(found_invite)

            # Update the sender's data with the updated invites list
            sender_ref.update({'invites': invites})

            return {'msg': f'Invite to {recipient_id} removed from invites list'}, 200
        else:
            return {'msg': 'Invite not found in the invites list'}, 404
    else:
        return {'msg': 'Sender not found'}, 404
    



