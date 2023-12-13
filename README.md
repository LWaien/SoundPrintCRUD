# SoundPrint CRUD API Readme

## API Overview

This API serves as the backend for the SoundPrint project, handling user account management and friend-related functionalities. The API interacts with a Firebase database (largely done in fb.py). The broader SoundPrint project is designed to deliver personalized concert recommendations to users, leveraging data from their Spotify listening habits and the shared music libraries of friends. Through its endpoints, the SoundPrint API facilitates essential operations, ensuring smooth user account management and friend-related functionalities within the SoundPrint platform.

*Note
Endpoints are only GET requests because it is easier to pass paramters when using Flask. These endpoints do not need to accept complex json data and the number of parameters is low so I just opted to use Flask GET endpoints for simplicity. 

## Endpoints

### 1. `/topartists/<spotify_user>` - HTTP GET

- Retrieves the top artists for a given Spotify user.
- **Input:** `spotify_user`
- **Output:** User's top artists.

### 2. `/previousEmail/<spotify_user>` - HTTP GET

- Checks if the previous email containing concert recommendations is still valid.
- **Input:** `spotify_user`
- **Output:**
  - If the email is still valid, returns the previous email.
  - If the email needs to be refreshed, returns appropriate status codes.
  - Handles various scenarios, including data loading and setup requests.

### 3. `/addEmailInfo` - HTTP GET

- Adds email information to the database.
- **Input:** `spotify_user`, `email`, `first_name`, `last_name`, `max_distance`, `location`
- **Output:**
  - If successful, returns a success message.
  - If the user already exists, returns a redirect to the login page.

### 4. `/createNewUser` - HTTP GET

- Creates a new user in the database.
- **Input:** `spotify_user`
- **Output:**
  - If successful, returns a success message.
  - If the user already exists, returns a redirect to the login page.

### 5. `/checkUser/<spotify_user>/` - HTTP GET

- Checks if a user exists in the database.
- **Input:** `spotify_user`
- **Output:**
  - If the user exists, returns a success message.
  - If the user does not exist, returns a not found message.

### 6. `/checkUser/<spotify_user>/<email>` - HTTP GET

- Checks if a user exists based on Spotify user and email.
- **Input:** `spotify_user`, `email`
- **Output:**
  - If the user exists, returns a success message.
  - If the user does not exist, returns a not found message.
  - Handles data loading scenarios.

### 7. `/searchUser/<spotify_user>` - HTTP GET

- Searches for users in the database based on a partial Spotify username.
- **Input:** `spotify_user`
- **Output:** List of matching users.

### 8. `/sendInvite/<sender_spotify>/<recipient_id>` - HTTP GET

- Sends a friend invitation from the sender to the recipient.
- **Input:** `sender_spotify`, `recipient_id`
- **Output:**
  - If successful, returns a success message.
  - If unsuccessful, returns an error message.

### 9. `/getInvites/<spotify_user>` - HTTP GET

- Retrieves pending friend invitations for a user.
- **Input:** `spotify_user`
- **Output:** List of pending invitations.

### 10. `/acceptInvite/<friend_user>/<friend_id>/<spotify_user>` - HTTP GET

- Accepts a friend invitation.
- **Input:** `friend_user`, `friend_id`, `spotify_user`
- **Output:**
  - If successful, returns a success message.
  - If unsuccessful, returns an error message.

### 11. `/friends/<spotify_user>` - HTTP GET

- Retrieves the list of friends for a user.
- **Input:** `spotify_user`
- **Output:** List of friends.

### 12. `/pending/<spotify_user>` - HTTP GET

- Retrieves the list of pending friend invitations for a user.
- **Input:** `spotify_user`
- **Output:** List of pending invitations.

## Database

The API interacts with a Firebase database to store user accounts, friend lists, and related information. Users can perform CRUD operations on their accounts and manage friend relationships through the provided endpoints.

Feel free to explore and integrate this API into your SoundPrint project for a seamless backend experience.
