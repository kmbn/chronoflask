import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from threading import Thread


# Create app
app = Flask(__name__)


# Register blueprints
from admin import admin
app.register_blueprint(admin, url_prefix='/admin')
from auth import auth
app.register_blueprint(auth, url_prefix='/auth')
from main import main
app.register_blueprint(main, url_prefix='/')


# Configure app
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


# Set up Bootstrap
bootstrap = Bootstrap(app)


# Set up email
mail = Mail(app)


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


# Run app
if __name__ == '__main__':
    app.run(debug=True)