from flask import Flask, session, redirect, url_for, render_template, flash, \
                  Blueprint
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from db import *
from setup import *

auth = Blueprint('auth', __name__)

from chronoflask import *





pwd_context = CryptContext(schemes=["pbkdf2_sha256"])

from auth_forms import ChangeEmailForm, ChangePasswordForm, \
                       RegistrationForm, LoginForm

'''# Decorator to prevent access by non-logged users.
def is_logged_in(func):
    def wrapper(*args):
        if not session.get('logged_in'):
            flash('You need to be logged in to do that.')
            return redirect(url_for('/login'))
        else:
            return func(*args)
    return wrapper
'''


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not get_record('auth', Query().email.exists()):
        flash('You need to register first.')
        return redirect(url_for('register'))
    if session.get('logged_in'):
        flash('Already logged in.')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        session['logged_in'] = True
        user_id = get_element_id('auth', Query().email == email)
        session['user_id'] = user_id
        flash('You are now logged in. User id: %s' % (user_id))
        return redirect(url_for('home'))
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    session['logged_in'] = None
    flash('You have been logged out.')
    return redirect(url_for('login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    # if not get_record('auth', Query().email.exists()):
    # need to handle the case where registration has already occured
    form = RegistrationForm()
    if form.validate_on_submit():
        password_hash = pwd_context.hash(form.password.data)
        # Create account and get creator id
        creator_id = insert_record('auth', {'email': form.email.data, \
                                   'password_hash': password_hash})
        # Create a chronofile
        default_chronofile_name = 'Chronofile'
        default_author_name = 'Chronologist'
        insert_record('admin', {'chronofile_name': default_chronofile_name, \
                      'author_name': default_author_name, \
                      'creator_id': creator_id})
        flash('Registration successful. You can login now.')
        return redirect(url_for('login'))
    return render_template('register', form=form)

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

@auth.route('/change_email', methods=['GET', 'POST'])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.new_email.data
        user_id = session.get('user_id')
        get_table('auth').update({'email': new_email}, eids=user_id)
        flash('Your email address has been updated.')
        return redirect(url_for('admin'))
    return render_template('change_email.html', form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        new_password_hash = pwd_context.hash(form.new_password.data)
        get_table('auth').update({'password_hash': new_password_hash}, \
                             eids=[session.get('user_id')])
        flash('Your password has been updated.')
        return redirect(url_for('admin'))
    return render_template('change_password', form=form)


def generate_confirmation_token(user_id, expiration=3600):
    serial = Serializer('secret_key', expiration)
    return serial.dumps({'confirm': user_id})