import os
from flask import Flask, session, g, redirect, url_for, render_template, \
                  flash, current_app
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from threading import Thread
from datetime import datetime
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from db import *
from main.views import main
from auth.views import auth
from admin.views import admin


app = Flask(__name__)


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


bootstrap = Bootstrap(app)
mail = Mail(app)


app.register_blueprint(main, url_prefix='/')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


if __name__ == '__main__':
    app.run(debug=True)