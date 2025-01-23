from flask import Blueprint, render_template, flash, url_for, redirect, request, session
from flask_login import current_user, login_required, login_user, logout_user
from skitunes import app, mail, db, login_manager
import requests
from oauthlib.oauth2 import WebApplicationClient
from skitunes.account.models import User
from skitunes.spotify.functions import authorize, get_user
from skitunes.variables.variables import *
from skitunes.auth.forms import (
    RegistrationForm, 
    LoginForm, 
    PasswordResetRequestForm, 
    PasswordResetForm
)
from skitunes.auth.functions import sanitize_form_data
import json
import urllib.parse as urllibparse
from urllib.parse import urlencode
from flask_mail import Mail, Message
import uuid

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
    form = LoginForm()  # Create the form
    return render_template('login.html', form=form)

@app.route('/login_local', methods=['GET', 'POST'])
def login_local():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    
    if request.method == 'POST':
        print("Login Form Submitted")
        print("Form data:", request.form)
        print("Form validate_on_submit():", form.validate_on_submit())
        
        if not form.validate_on_submit():
            print("Form Errors:")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
        
        if form.validate_on_submit():
            # Debug: Check email exists
            user = User.query.filter_by(email=form.email.data).first()
            
            if user:
                print(f"User found: {user.email}")
                print(f"User ID: {user.user_id}")
                
                # More detailed password verification
                from werkzeug.security import check_password_hash
                print("Manual password verification:")
                print(f"Stored hash: {user.pwd}")
                print(f"Attempted password: {form.password.data}")
                manual_check = check_password_hash(user.pwd, form.password.data)
                print(f"Manual check result: {manual_check}")
                
                # Test with different methods
                print("Built-in method check:")
                builtin_check = user.check_password(form.password.data)
                print(f"Built-in check result: {builtin_check}")
            else:
                print(f"No user found with email: {form.email.data}")
            
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                print("Login failed: Invalid credentials")
                flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        print("Form submitted")
        print("Form data:", sanitize_form_data(request.form))
        print("Form validate_on_submit():", form.validate_on_submit())
        
        if not form.validate_on_submit():
            print("Form Errors:")
            for field, errors in form.errors.items():
                if field not in ['password', 'confirm_password']:
                    print(f"{field}: {errors}")
                else:
                    print(f"{field}: [REDACTED]")
        
        if form.validate_on_submit():
            try:
                # Generate user_id before creating user
                user_id = User.generate_next_user_id()
                
                user = User.create(
                    user_id=user_id,  # Pass the generated user_id
                    name=form.name.data, 
                    email=form.email.data, 
                    profile_pic=None,
                    pwd=form.password.data
                )

                login_user(user)
                flash('Your account has been created! You are now logged in.', 'success')
                return redirect(url_for('home'))
            
            except ValueError as e:
                # Make sure error message doesn't contain password
                safe_error = str(e)
                if 'password' in safe_error.lower():
                    safe_error = "An error occurred during registration"
                flash(safe_error, 'danger')
                return redirect(url_for('home'))  # Redirect to home with error message
            except Exception as e:
                # Handle any other unexpected errors
                flash('An unexpected error occurred during registration. Please try again.', 'danger')
                return redirect(url_for('home'))
    
    return render_template('register.html', form=form)

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
    session.clear()
    return redirect(url_for("home"))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate reset token
            reset_token = user.generate_reset_token()
            
            # Send reset email
            reset_url = url_for('reset_password', token=reset_token, _external=True)
            
            msg = Message('Password Reset Request',
                          sender='your-email@gmail.com',  # Your email
                          recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.
'''
            
            try:
                mail.send(msg)
                flash('An email has been sent with instructions to reset your password.', 'info')
            except Exception as e:
                flash('Failed to send reset email. Please try again later.', 'danger')
        else:
            flash('No account found with that email.', 'warning')
    
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Verify the token
    user = User.verify_reset_token(token)
    
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_password_request'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Update the user's password
        user.pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Clear the reset token
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login_local'))
    
    return render_template('reset_password.html', form=form)

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