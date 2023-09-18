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
    #passing key to retrieve top artists for the user 
    previous_email = fb.getpreviousEmail(keys)
    #return user's top_artist(s)
    return previous_email


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