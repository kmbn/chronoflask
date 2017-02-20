import os
from flask import Flask
from flask_mail import Mail
from flask_bootstrap import Bootstrap


# Create app
app = Flask(__name__)


# Register blueprints
from app.admin import admin
app.register_blueprint(admin, url_prefix='/admin')
from app.auth import auth
app.register_blueprint(auth, url_prefix='/admin')
from app.main import main
app.register_blueprint(main, url_prefix='/')

from app.main.views import *
from app.auth.views import *
from app.main.errors import *


# Configure app
app.config['DEBUG'] = int(os.environ.get('DEBUG'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[Chronoflask]'
app.config['MAIL_SENDER'] = 'Chronoflask <admin@chronoflask.com>'
app.config['DEFAULT_NAME'] = 'Chronoflask'
app.config['DEFAULT_AUTHOR'] = 'Chronologist'


# Set up Mail
mail = Mail(app)

# Set up Bootstrap
bootstrap = Bootstrap(app)