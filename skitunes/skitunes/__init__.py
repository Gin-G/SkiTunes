from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .logs.functions import LogSetup
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config.from_pyfile('config.py')
mail = Mail(app)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_local'  # specify the login route

# Logging is stopping the app from running, removed it for now to get a working version that can be troubleshot additionally later
# Configure the logging setup as defined in log functions module and apply to the app
#logs = LogSetup()
#logs.init_app(app)

from skitunes.main import views
from skitunes.auth import views
from skitunes.imports import views
from skitunes.metrics import views
#from skitunes.logs import views