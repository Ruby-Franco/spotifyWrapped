import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, redirect, request, session, url_for, jsonify
import os 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY') 

# Set up Spotify OAuth credentials
sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope="user-library-read user-top-read"
)

@app.route('/')
def home(): 
    session.clear()
    auth_url = sp_oauth.get_authorize_url()
    print(f"Authorizatoin URL: {auth_url}")
    return redirect(auth_url) # redirect to spotify login

@app.route('/callback')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"Spotify OAuth Error: {error}"

    try:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info  # Save the token in the session
        return redirect('/success')  # Redirect to a success route
    except Exception as e:
        print(f"Error fetching access token: {e}")
        return "Error: Could not authenticate with Spotify."

@app.route('/success')
def success(): 
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/')
    #display the access toekn fo r testing
    return f"Logged in! Access Token: {token_info['access_token']}"


@app.route('/logout')
def logout():
    session.clear()
    print("Session cleared in logout")  # Log when session is cleared in logout
    return redirect('/')

def get_token():
    token_info = session.get('token_info', None)  # Get token info from the session
    if not token_info:
        return None

    if sp_oauth.is_token_expired(token_info):  # Check if the token is expired
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])  # Refresh the token
        session['token_info'] = token_info  # Save the new token

    return token_info

if __name__ == "__main__":
    app.run(debug=True)
