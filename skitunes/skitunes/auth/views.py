from flask import Blueprint, render_template, flash, url_for, redirect, request, session
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
from skitunes import app
import requests
from oauthlib.oauth2 import WebApplicationClient
from skitunes.account.models import User
from skitunes.spotify.functions import authorize
import os
import json
import urllib.parse as urllibparse

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

redirect_uri_url = "https://www.skimoviesongs.com/login/callback"

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('sign_up.html')

@app.route('/login')
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri_url,
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
        redirect_url="https://www.skimoviesongs.com/login",
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
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        user = User.create(unique_id, users_name, users_email, picture)
    else:
        user = User.get(unique_id)
    if user == None:
        user = User.create(unique_id, users_name, users_email, picture)
    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("home"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/spotfy/auth')
def spotify_auth():
    SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
    SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')
    SCOPE = "playlist-modify-public playlist-modify-private user-read-recently-played user-top-read"
    client_id = os.environ.get("SPOTIFY_CLIENT_ID", None)
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": 'https://www.skimoviesongs.com/spotify/login/q',
        "scope": SCOPE,
        # "state": STATE,
        # "show_dialog": SHOW_DIALOG_str,
        "client_id": client_id,
    }
    URL_ARGS = "&".join(["{}={}".format(key, urllibparse.quote(val))
                    for key, val in list(auth_query_parameters.items())])
    AUTH_URL = "{}/?{}".format(SPOTIFY_AUTH_URL, URL_ARGS)
    
    return redirect(AUTH_URL)

@app.route('/spotfy/login/q')
def spotify_login():
    auth_token = request.args['code']
    header = authorize(auth_token)
    session['auth_header'] = header['header']
    return redirect(url_for("home"))