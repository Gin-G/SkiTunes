from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_local'

# Only allow insecure OAuth transport in debug/dev mode
if os.environ.get('FLASK_DEBUG', '1') == '1':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from skitunes.main import views
from skitunes.auth import views
from skitunes.imports import views
from skitunes.metrics import views
from skitunes.crowd import views
from skitunes.crowd import models as crowd_models  # noqa — needed for migrations
