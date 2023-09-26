from flask import Flask, redirect, url_for, request,jsonify, make_response
from urllib.parse import urlencode
import fb


CLIENT_ID = "32f3ca3f815c4b7f91335ffeb5d90f7d"
CLIENT_SECRET = "3f882c04f6824a68b45b251ff922488a"


app = Flask(__name__)


@app.route("/topartists/<spotify_user>",methods=['GET'])
def topartists(spotify_user):
    #retrieving user key that we want to query
    keys = fb.searchDb('spotify_user',spotify_user)
    #passing key to retrieve top artists for the user 
    top_artists = fb.get_topartists(keys)
    #return user's top_artists
    return top_artists

@app.route("/previousEmail/<spotify_user>",methods=['GET'])
def previousEmail(spotify_user):
    #retrieving user key that we want to query
    keys = fb.searchDb('spotify_user',spotify_user)
    #check that the previous email was made within the past 7 days. Otherwise we need to call api to generate a new one
    refreshFlag = fb.checkPrevListDate(keys)
    checkRecSetup = fb.checkRecSetup(keys)
    previous_email = fb.getpreviousEmail(keys)

        
    #returns status codes that represent date refresh needs so that the front end can make an async call to refresh the concert list if it is out of date (404 status code)
    if refreshFlag is True:
        print("previous list sent")
        return make_response(previous_email,200)
    else:
        #if there's no list to pull but rec is setup, the concerts should be loading
        if previous_email is None and checkRecSetup is True:
            print("Previous list data not available, but loading")
            return make_response({'msg':'data loading'},403)
        #if no concerts at all and no set up, prompt user to set them up
        if previous_email is None and checkRecSetup is False:
            print("Previous list data not available, requesting to set up recs")
            return make_response({'msg':'data loading'},402)
        #else, refresh flag is false but everything is good. Just means list is not due for an update
        else:
            print("Previous list not due for a refresh")
            return make_response(previous_email,404)


@app.route("/addEmailInfo",methods=['GET'])
def addEmailInfo():
    #collect data from request
    spotify_user = request.args.get('spotify_user')
    email = request.args.get('email')
    first_name = request.args.get('fname')
    last_name = request.args.get('lname')
    max_distance = request.args.get('max_distance')
    location = [request.args.get('location')]

    #attempt to push to db
    try:
        response_msg,response_code = fb.insertEmailInfo(spotify_user, email,first_name,last_name,max_distance,location)
        #if response code is 409 (user exists), front end should redirect to login
        return make_response(response_msg,response_code)
    except:
        #return 404 if db system fails
        return make_response({'msg':"Unable to connect to the database"},404)


@app.route("/createNewUser",methods=['GET'])
def createNewUser():
    spotify_user = request.args.get('spotify_user')
    try:
        fb.createNewUser(spotify_user)
        #if response code is 409 (user exists), front end should redirect to login
        return make_response({'msg':'user was successfully added to the the database'},201)
    except:
        #return 404 if db system fails
        return make_response({'msg':"Unable to connect to the database"},404)


@app.route("/checkUser/<spotify_user>/",methods=['GET'])
def checkUser2(spotify_user):
    keys = fb.searchDb('spotify_user',spotify_user)
    if keys:
        return make_response({'msg':'User exists'},200)
    else:
        return make_response({'msg':'User not found'},404)

   
@app.route("/checkUser/<spotify_user>/<email>",methods=['GET'])
def checkUser(spotify_user,email):
    keys = fb.searchDb('spotify_user',spotify_user)
    if keys:
        return make_response({'msg':'User exists'},200)
    
    #print(email)
    #first check if user exists
    user_keys = fb.searchDb('email',email)
    if user_keys:
        #second, check if spotify data loaded. Give according resp so 
        #front end can display
        spotify_keys = fb.searchDb('spotify_user',spotify_user)
        if spotify_keys:
            return make_response({'msg':'User exists'},200)
        else:
            return make_response({'msg':'data still loading'},201)
    else:
        print('user does not exist')
        return make_response({'msg':'User does not have an account'},404)
    
@app.route("/searchUser/<spotify_user>",methods=['GET'])
def searchUser(spotify_user):
    keys,usernames = fb.searchDbForUser('spotify_user',spotify_user)
    searchlist = []
    for i in range(len(keys)):
        user = {'id':keys[i],'spotify_user':usernames[i]['spotify_user']}
        searchlist.append(user)
    return make_response({'users':searchlist},200)

@app.route("/sendInvite/<sender_spotify>/<recipient_id>")
def sendInvite(sender_spotify,recipient_id):
    try:
        resp,code = fb.sendInv(sender_spotify,recipient_id)
        return make_response({'msg':resp},code)
    except:
        return make_response({'msg':'Failed to send friend request'},404)

if __name__ == "__main__":
    app.run(debug=True)