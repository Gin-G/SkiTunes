from flask import Flask
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .logs.functions import LogSetup
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config.from_pyfile('config.py')
mail = Mail(app)

db = SQLAlchemy(app)

# Logging is stopping the app from running, removed it for now to get a working version that can be troubleshot additionally later
# Configure the logging setup as defined in log functions module and apply to the app
#logs = LogSetup()
#logs.init_app(app)

from skitunes.main import views
from skitunes.auth import views
#from skitunes.logs import views