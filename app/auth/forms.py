from flask import session
from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, EqualTo
from db import *
from .views import pwd_context


# Custom validators
def account_exists(form, field):
    user = get_record('auth', Query().email == field.data)
    if not user:
        raise ValidationError('Create an account first.')


def email_exists(form, field):
    user = get_record('auth', Query().email == field.data)
    if not user:
        raise ValidationError('Please verify that you typed your email \
            correctly.')


def authorized(form, field):
    '''Verify user through password.'''
    user = get_table('auth').get(eid=session.get('user_id'))
    if not pwd_context.verify(field.data, user['password_hash']):
        raise ValidationError('Invalid login credentials. Please try again.')


class PasswordCorrect(object):
    '''Verify email/password combo before validating form.'''
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            email = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        user = get_record('auth', Query().email == email.data)
        if not pwd_context.verify(field.data, user['password_hash']):
            raise ValidationError('Invalid password. Please try again.')


class LoginForm(Form):
    email = StringField('Email:', validators=[Required(), Email(), \
                        account_exists])
    password = PasswordField('Password:', validators=[Required(), \
                             PasswordCorrect('email')])
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    email = StringField('Enter your email address:', \
                        validators=[Required(), Email()])
    password = PasswordField('Create a password:', validators=[Required(), \
                             Length(min=12)])
    submit = SubmitField('Create account')


class ChangeEmailForm(Form):
    password = PasswordField('Enter your password:', validators=[Required(), \
                             authorized])
    new_email = StringField('New email address:', \
                            validators=[Required(), Email(), \
                            EqualTo('verify_email', \
                            message='Emails must match')])
    verify_email = StringField('Re-enter new email address:', \
                               validators=[Required(), Email()])
    submit = SubmitField('Change email')


class ChangePasswordForm(Form):
    current_password = PasswordField('Your current password:', \
                                     validators=[Required(), authorized])
    new_password = PasswordField('Your new password:', validators=[Required(), \
                                 Length(min=12), EqualTo('verify_password', \
                                 message='New passwords must match.')])
    verify_password = PasswordField('Re-enter new password:', \
                                    validators=[Required(), Length(min=12)])
    submit = SubmitField('Change password')


class ResetPasswordForm(Form):
    email = StringField('Your registered email address:',
                        validators=[Required(), Email(), email_exists])
    submit = SubmitField('Request password reset link')


class SetNewPasswordForm(Form):
    new_password = PasswordField('Enter your new password:', validators=[Required(), \
                                 Length(min=12), EqualTo('verify_password', \
                                 message='New passwords must match.')])
    verify_password = PasswordField('Re-enter new password:', \
                                    validators=[Required(), Length(min=12)])
    submit = SubmitField('Set new password')