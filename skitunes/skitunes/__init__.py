from flask import Flask
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

from skitunes.main import views
from skitunes.auth import views

