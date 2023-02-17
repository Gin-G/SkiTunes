from flask import Blueprint, render_template, flash, url_for, redirect, request, session
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
from skitunes import app
import requests
from oauthlib.oauth2 import WebApplicationClient
from skitunes.account.models import User
from skitunes.spotify.functions import authorize, get_user
from skitunes.variables.variables import *
import os
import json
import urllib.parse as urllibparse
from urllib.parse import urlencode

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('sign_up.html')

@app.route('/login_url')
def login_url():
    return render_template('login.html')

@app.route('/login_local', methods=["GET","POST"])
def login_local():
    flash('Local login is being worked on currently but not yet available')
    return render_template('skitunes.html')

@app.route('/signup')
def signup():
    flash('Registration is being worked on currently but not yet available')
    return render_template('skitunes.html')

@app.route('/login')
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=google_redirect_uri_url,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route('/login/callback')
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=google_redirect_uri_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!

    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        pwd = 'Nonethisisgoogle'
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        user = User.create(unique_id, users_name, users_email, picture, pwd)
    else:
        user = User.get(unique_id)
    if user == None:
        try:
            user = User.create(unique_id, users_name, users_email, picture, pwd)
        except:
            return redirect(url_for('home'))
    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("spotify_auth"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/spotify/auth', methods=["GET", "POST"])
def spotify_auth():
    auth_query_parameters = urlencode({
        "response_type": "code",
        "redirect_uri": spotify_redirect_uri_url,
        "scope": SCOPE,
        "state": STATE,
        "show_dialog": 'true',
        "client_id": client_id,
    })
    url = SPOTIFY_AUTH_URL + auth_query_parameters
    
    return redirect(url)

@app.route('/spotify/callback', methods=["GET", "POST"])
def spotify_callback():
    code = request.args.get("code")
    state =  request.args.get("state")
    response = authorize(code)
    try:
        access_token = response['access_token']
        session['spotify_access_token'] = access_token
        expires = response['expires_in']
        refresh_token = response['refresh_token']
        session['spotify_refresh_token'] = refresh_token
    except KeyError:
        pass
    user = get_user()
    user = user.json()
    try:
        spotify_user_id = user['id']
        display_name = user['display_name']
        session['display_name'] = display_name
        session['spotify_user_id'] = spotify_user_id
    except KeyError:
        pass    
    return redirect(url_for('home'))