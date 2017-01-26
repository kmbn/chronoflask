from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from mocksession import Session
from db import *


##############################################################################
# TinyAuth
##############################################################################
pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


def is_logged_in(func):
    def wrapper(*args):
        if not Session.s['logged_in']:
            print('You need to be logged in to do that.')
            return login()
        else:
            return func(*args)
    return wrapper


def login():
    if not get_record('auth', Query().email.exists()):
        print('You need to register first.')
        return False
    if not Session.s['logged_in']:
        email = input('Enter email: ')
        password = input('Enter password: ')
        user = get_record('auth', Query().email == email)
        if not user:
            print('That account does not exist. Please register.')
            return False
        if not pwd_context.verify(password, user['password_hash']):
            print('Invalid password. Please try again.')
            return False
        else:
            Session.s['logged_in'] = True
            Session.s['user_id'] = get_element_id('auth',\
                                                  Query().email == email)
            print('You are now logged in. User id: %s' % \
                  (Session.s['user_id']))
            return True
    else:
        print('Already logged in.')
        return True


@is_logged_in
def logout():
    Session.s['logged_in'] = None
    print('You have been logged out.')
    return True


def register():
    if not get_record('auth', Query().email.exists()):
        email = input('Enter email: ')
        password = input('Enter password: ')
        password_hash = pwd_context.hash(password)
        creator_id = insert_record('auth', {'email': email, \
                                   'password_hash': password_hash})
        default_chronofile_name = 'Chronofile'
        default_author_name = 'Chronologist'
        insert_record('admin', {'chronofile_name': default_chronofile_name, \
                      'author_name': default_author_name, \
                      'creator_id': creator_id})
        print('Registration successful')
        return True
    else:
        print('There is already a user registered.')
        return True

'''
def reset_password(token=None):
    if not token:
        email = input('Enter email to receive password reset token: ')
        if not get_record('auth', Query().email == email):
            print('That email is not registered.')
            return get_input()
        user_id = get_element_id('admin', email)
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
            update_record('auth', {'password_hash': new_password_hash}, \
                              eids=data.get('confirm'))
            print('Your password has been updated.')
            return get_input()
'''

@is_logged_in
def change_email():
    password = input('Enter password: ')
    user = get_table('auth').get(eid=Session.s['user_id'])
    if not pwd_context.verify(password, user['password_hash']):
        print('Invalid password. Please try again.')
        return False
    new_email = input('Enter new email: ')
    get_table('auth').update({'email': new_email}, eids=[Session.s['user_id']])
    print('Your email address has been updated.')
    return True


@is_logged_in
def change_password():
    current_password = input('Enter current password: ')
    user = get_table('auth').get(eid=Session.s['user_id'])
    if not pwd_context.verify(current_password, user['password_hash']):
        print('Invalid password. Please try again.')
        return False
    new_password = input('Enter new password: ')
    verify_password = input('Re-enter new password: ')
    if new_password != verify_password:
        print('Passwords do not match.')
        return False
    new_password_hash = pwd_context.hash(new_password)
    get_table('auth').update({'password_hash': new_password_hash}, \
                             eids=[Session.s['user_id']])
    print('Your password has been updated.')
    return True


def generate_confirmation_token(user_id, expiration=3600):
    serial = Serializer('secret_key', expiration)
    return serial.dumps({'confirm': user_id})