from flask import Flask, session, redirect, url_for, render_template, flash, \
                  Blueprint, current_app
from passlib.context import CryptContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import ujson
from db import *


pwd_context = CryptContext(schemes=["pbkdf2_sha256"])
from .forms import ChangeEmailForm, ChangePasswordForm, \
                       RegistrationForm, LoginForm, ResetPasswordForm, \
                       SetNewPasswordForm

auth = Blueprint('auth', __name__)

from chronoflask import send_email

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
        return redirect(url_for('auth.register'))
    if session.get('logged_in'):
        flash('Already logged in.')
        return redirect(url_for('main.browse_all_entries'))
    form = LoginForm()
    if form.validate_on_submit():
        session['logged_in'] = True
        user_id = get_element_id('auth', Query().email == form.email.data)
        session['user_id'] = user_id
        flash('You are now logged in. User id: %s' % (user_id))
        return redirect(url_for('main.browse_all_entries'))
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    session['logged_in'] = None
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))


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
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user_id = get_element_id('auth', Query().email == email)
        token = generate_confirmation_token(user_id)
        send_email(email, 'Link to reset your password',
                   'email/reset_password', token=token)
        flash('Your password reset token has been sent.')
        return redirect(url_for('admin.get_details'))
    return render_template('reset_password.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def confirm_password_reset(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        flash('The password reset link is invalid or has expired.')
        return redirect(url_for('auth.request_reset'))
    if not data.get('confirm'):
        flash('The password reset link is invalid or has expired.')
        return redirect(url_for('auth.request_reset'))
    user_id = data.get('confirm')
    form = SetNewPasswordForm()
    if form.validate_on_submit():
        new_password_hash = pwd_context.hash(form.new_password.data)
        get_table('auth').update({'password_hash': new_password_hash}, \
                                 eids=[user_id])
        flash('Password updated—you can now log in.')
        return redirect(url_for('auth.login'))
    return render_template('set_new_password.html', form=form, token=token)


@auth.route('/change_email', methods=['GET', 'POST'])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.new_email.data
        user_id = session.get('user_id')
        get_table('auth').update({'email': new_email}, eids=user_id)
        flash('Your email address has been updated.')
        return redirect(url_for('admin.get_details'))
    return render_template('change_email.html', form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        new_password_hash = pwd_context.hash(form.new_password.data)
        get_table('auth').update({'password_hash': new_password_hash}, \
                             eids=[session.get('user_id')])
        flash('Your password has been updated.')
        return redirect(url_for('admin.get_details'))
    return render_template('change_password.html', form=form)


def generate_confirmation_token(user_id, expiration=3600):
    serial = Serializer(current_app.config['SECRET_KEY'], expiration)
    return serial.dumps({'confirm': user_id})