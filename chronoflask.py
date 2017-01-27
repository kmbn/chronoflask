'''
Chronoflask:
A minimalist diary/journal application using Python 3, Flask, and TinyDB
inspired by Warren Ellis's Chronofile Minimal and Buckminster Fuller's
Dymaxion Chronofile.

Add new entries (with or witout hashtags) in a single input field. Each
entry is stored with a UTC created-on timestamp.

View recent entries, view all entries for a single day or date-range
(chronologically), view a single entry, view all entries associated with
a tag, and view a list of tags.

Private by default; can be made public.
'''
from flask import Flask, session, g, redirect, url_for, render_template, flash
from flask_bootstrap import Bootstrap
from datetime import datetime
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from setup import *
from db import *
from main.views import main
from auth.views import auth
from admin.views import admin


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')


# Load default config and override config from an environment variable
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'base.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    # USERNAME='admin',
    # PASSWORD='default'
))
app.config.from_envvar('APP_SETTINGS', silent=True)


##############################################################################
# Main input and parser
##############################################################################
def get_input():
    raw_entry = input('> ')
    timestamp = datetime.utcnow()
    return parse_input(raw_entry, timestamp)

'''
def parse_input(raw_entry, current_time):
    if raw_entry == 'browse all':
        return browse_all_entries()
    elif raw_entry == 'quit':
        return quit()
    elif raw_entry[:3] == 't: ':
        return view_single_entry(raw_entry[3:])
    elif raw_entry[:5] == 'tag: ':
        return view_entries_for_tag(raw_entry[5:])
    elif raw_entry[:5] == 'day: ':
        return view_entries_for_day(raw_entry[5:])
    elif raw_entry == 'register':
        register()
        return get_input()
    elif raw_entry == 'login':
        login()
        return get_input()
    elif raw_entry == 'logout':
        logout()
        return get_input()
    elif raw_entry == 'change email':
        change_email()
        return get_input()
    elif raw_entry == 'change password':
        change_password()
        return get_input()
    elif raw_entry[:14] == 'reset password':
        reset_password(raw_entry[15:])
        return get_input()
    elif raw_entry == 'about':
        get_chronofile_details()
        return get_input()
    elif raw_entry == 'rename chrono':
        rename_chronofile()
        return get_input()
    elif raw_entry == 'rename author':
        rename_author()
        return get_input()
    else:
        return process_entry(raw_entry, current_time)
'''

##############################################################################
# The app
##############################################################################



if __name__ == '__main__':
    #init_db()
    app.run(debug=True)