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

from tinydb import TinyDB, Query, where
from datetime import datetime
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson


##############################################################################
# Setup DB and queries
##############################################################################
def get_db():
    db = TinyDB('chronofile_db.json')
    return db


def tiny_search(query):
    ts = get_db().search(query)
    return ts


def tiny_get(query):
    tg = get_db().get(query)
    return tg
##############################################################################


def get_input():
    raw_entry = input('> ')
    current_time = datetime.utcnow()
    return parse_input(raw_entry, current_time)


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
        return register()
    elif raw_entry == 'login':
        return login()
    elif raw_entry == 'logout':
        return logout()
    elif raw_entry == 'change email':
        return change_email()
    elif raw_entry == 'change password':
        return change_password()
    elif raw_entry[:14] == 'reset password':
        return reset_password(raw_entry[15:])
    elif raw_entry == 'about':
        return get_chronofile_details()
    elif raw_entry == 'rename chrono':
        return rename_chronofile()
    elif raw_entry == 'rename author':
        return rename_author()
    else:
        return process_entry(raw_entry, current_time)
        #process_entry(raw_entry, current_time)


def process_entry(raw_entry, current_time):
    is_logged_in()
    clean_entry = clean_up_entry(raw_entry)
    timestamp = create_timestamp(current_time)
    tags = find_and_process_tags(raw_entry)
    return create_new_entry(clean_entry, timestamp, tags)


def clean_up_entry(raw_entry):
    '''Uppercase the first letter of the entry and remove any tags from the
    end of the entry. (Tags in the body of the entry will be considered
    part of the content and left alone.)
    '''
    clean_entry = raw_entry[0].upper() + raw_entry[1:]
    return clean_entry


def create_timestamp(current_time):
    '''
    Convert datetime object to string for use with JSON.
    May not be necessary with alterate storage or extensions.
    '''
    timestamp = datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S')
    return timestamp


def find_and_process_tags(raw_entry):
    '''
    Extract all hashtags from the entry.
    '''
    bag_of_words = raw_entry.split()
    tags = []
    punctuation = ['.', ',']
    for i in bag_of_words:
        if i[0] == '#':
            if i[-1] in punctuation: # Clean tag if it ends w/ punctuation
                tags.append(i[:-1])
            else:
                tags.append(i)
    return tags


def create_new_entry(clean_entry, timestamp, tags):
    get_db().insert({'entry': clean_entry, 'timestamp': timestamp, \
                    'tags': tags})
    return get_input()


def browse_all_entries():
    is_logged_in()
    result = get_db().all()
    if not result:
        print('Nothing in the chronofile yet.')
    else:
        for i in reversed(result):
            print('%s: %s :: filed under %s' % (i['timestamp'], \
                  i['entry'], i['tags']))
    return get_input()


def view_single_entry(timestamp):
    '''
    Return a single entry based on given timestamp
    '''
    is_logged_in()
    result = tiny_get(Query().timestamp == timestamp)
    if not result:
        print('No entry for that timestamp.')
    else:
        print('%s: %s :: filed under %s' % (result['timestamp'], \
              result['entry'], result['tags']))
    return get_input()


def view_entries_for_tag(tag):
    '''
    Return entries for given tag in chronological order.
    '''
    is_logged_in()
    result = tiny_search(Query().tags.all(tag))
    # result = get_db().search(Query().tags.all(tag))
    if not result:
        print('No entries for that tag.')
    else:
        for i in result:
            print('%s: %s :: filed under %s' % (i['timestamp'], \
                  i['entry'], i['tags']))
    return get_input()


def view_entries_for_day(day):
    '''
    Returns entries for given day in chronological order.
    '''
    is_logged_in()
    result = tiny_search(Query().timestamp.all([day]))
    if not result:
        print('No entries for that day.')
    else:
        for i in result:
            print('%s: %s :: filed under %s' % (i['timestamp'], \
                  i['entry'], i['tags']))
    return get_input()


##############################################################################
# TinyAuth
##############################################################################
pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


class Session():
    s = {'logged_in': None, 'user_id': None}


def get_db():
    db = TinyDB('chronofile_db.json')
    return db


def get_table(table_name):
    table = get_db().table(table_name)
    return table


def get_record(table_name, query):
    result = get_table(table_name).get(query)
    return result


def get_auth():
    db = TinyDB('chronofile_db.json')
    auth = db.table('auth')
    return auth


def auth_get(query):
    ag = get_auth().get(query)
    return ag


def auth_insert(query):
    ai = get_auth().insert(query)
    return True


def auth_update(field, query):
    au = get_auth().update(field, query)
    return True


def get_user_id(email):
    element = auth_get(Query().email == email)
    user_id = element.eid
    return user_id


def login():
    if not auth_get(Query().email.exists()):
        print('You need to register first.')
        return get_input()
    if not Session.s['logged_in']:
        email = input('Enter email: ')
        password = input('Enter password: ')
        user = auth_get(Query().email == email)
        if not user:
            print('That account does not exist. Please register.')
            return get_input()
        if not pwd_context.verify(password, user['password_hash']):
            print('Invalid password. Please try again.')
            return get_input()
        else:
            Session.s['logged_in'] = True
            Session.s['user_id'] = get_user_id(email)
            print('You are now logged in. User id: %s' % \
                  (Session.s['user_id']))
            return get_input()
    else:
        print('Already logged in.')
        return get_input()


def logout():
    if not Session.s['logged_in']:
        print('You are already logged out')
        return get_input()
    else:
        Session.s['logged_in'] = None
        print('You have been logged out.')
        return get_input()


def register():
    if not auth_get(Query().email.exists()):
        email = input('Enter email: ')
        password = input('Enter password: ')
        password_hash = pwd_context.hash(password)
        auth_insert({'email': email, 'password_hash': password_hash})
        password = None
        default_chronofile_name = 'Chronofile'
        default_author_name = 'Chronologist'
        admin_insert({'chronofile_name': default_chronofile_name, \
                     'author_name': default_author_name, \
                     'creator_id': get_user_id(email)})
        print('Registration successful')
        return get_input()
    else:
        print('There is already a user registered.')
        return get_input()


def reset_password(token=None):
    if not token:
        email = input('Enter email to receive password reset token: ')
        if not auth_get(Query().email == email):
            print('That email is not registered.')
            return get_input()
        user_id = get_user_id(email)
        token = generate_confirmation_token(user_id)
        print('Your password reset token is %s' % (token))
        return get_input()
    serial = Serializer('secret_key')
    user_id = Session.s['user_id']
    print(token)
    try:
        data = serial.loads(token)
    except:
        print('The token is invalid or has expired.')
        return get_input()
    else:
        if data.get('confirm') != user_id:
            print('The token is invalid or has expired.')
            return get_input()
        else:
            new_password = input('Enter new password: ')
            verify_password = input('Re-enter new password: ')
            if new_password != verify_password:
                print('Passwords do not match.')
                return get_input()
            new_password_hash = pwd_context.hash(new_password)
            get_auth().update({'password_hash': new_password_hash}, \
                              eids=data.get('confirm'))
            print('Your password has been updated.')
            return get_input()


def change_email():
    is_logged_in()
    password = input('Enter password: ')
    user = get_auth().get(eid=Session.s['user_id'])
    if not pwd_context.verify(password, user['password_hash']):
        print('Invalid password. Please try again.')
        return get_input()
    new_email = input('Enter new email: ')
    get_auth().update({'email': new_email}, eids=[Session.s['user_id']])
    print('Your email address has been updated.')
    return get_input()


def change_password():
    is_logged_in()
    current_password = input('Enter current password: ')
    user = get_auth().get(eid=Session.s['user_id'])
    if not pwd_context.verify(current_password, user['password_hash']):
        print('Invalid password. Please try again.')
        return get_input()
    new_password = input('Enter new password: ')
    verify_password = input('Re-enter new password: ')
    if new_password != verify_password:
        print('Passwords do not match.')
        return get_input()
    new_password_hash = pwd_context.hash(new_password)
    get_auth().update({'password_hash': new_password_hash}, \
                      eids=[Session.s['user_id']])
    print('Your password has been updated.')
    return get_input()


def generate_confirmation_token(user_id, expiration=3600):
    serial = Serializer('secret_key', expiration)
    return serial.dumps({'confirm': user_id})


def is_logged_in():
    if not Session.s['logged_in']:
        print('You need to be logged in to do that.')
        return get_input()
    else:
        return True

##############################################################################

##############################################################################
# TinyAdmin
##############################################################################
def get_admin():
    db = TinyDB('chronofile_db.json')
    admin = db.table('admin')
    return admin


def admin_get(query):
    ag = get_admin().get(query)
    return ag


def admin_update(field, query):
    au = get_admin().update(field, query)
    return True


def admin_insert(query):
    ai = get_admin().insert(query)
    return True


def get_chronofile_details():
    is_logged_in()
    result = get_admin().all()
    print('Chronofile name: %s' % (result[0]['chronofile_name']))
    print('Chronofile author: %s' % (result[0]['author_name']))
    return get_input()


def rename_chronofile():
    is_logged_in()
    new_name = input('Enter new name for chronofile: ')
    admin_update({'chronofile_name': new_name}, \
                 Query().creator_id == Session.s['user_id'])
    return get_input()


def rename_author():
    is_logged_in()
    new_name = input('Enter new author name: ')
    admin_update({'author_name': new_name}, \
                 Query().creator_id == Session.s['user_id'])
    return get_input()

##############################################################################


get_input()