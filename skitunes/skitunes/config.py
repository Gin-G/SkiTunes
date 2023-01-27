import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///skitunes.db'
SECRET_KEY = 'steve wants to ski in a tipsy elves onsie'
SQLALCHEMY_TRACK_MODIFICATIONS = False 

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'NickCo7@gmail.com'
MAIL_DEFAULT_SENDER = 'NickCo7@gmail.com'
MAIL_PASSWORD = os.environ.get('PEANUT_BRITTLE')
MAIL_USE_TLS = False
MAIL_USE_SSL = True
LOG_TYPE = "watched"
LOG_LEVEL = "INFO"
LOG_DIR = "./log"
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_COPIES = 3
APP_LOG_NAME = "skimoviesongs.log"
WWW_LOG_NAME = "skimoviesongs_www.log"