#!/usr/bin/env python

from flask import Flask, render_template, Response, redirect, url_for, request, session, abort, flash, send_from_directory, jsonify
from wtforms import TextField, PasswordField, StringField, SubmitField, SelectField, validators
from wtforms.fields.html5 import DateField, IntegerField
from flask_wtf import FlaskForm, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from functools import wraps
from datetime import datetime, timedelta
from Log import Log, LogType
import ErrorHandler

import bcrypt
import os
import sys
import traceback

import config


_log = Log()

CREDS = config.get_creds('envs.json', crypt=False)

app = Flask(__name__)

moment = Moment(app)

app.config['ADMIN_ROLE_ID'] = CREDS['ADMIN_ROLE_ID']
app.config['APPLICATION_VERSION'] = CREDS['APPLICATION_VERSION']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = CREDS['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SQLALCHEMY_DATABASE_URI'] = CREDS['SQLALCHEMY_DATABASE_URI']
app.config['STANDARD_ROLE_ID'] = CREDS['STANDARD_ROLE_ID']
app.config['SYSTEM_VALUES_NOTIFICATIONS'] = CREDS['SYSTEM_VALUES_NOTIFICATIONS']

db = SQLAlchemy(app)

# Our models, import here after db has been instantiated
import Reward, Role, User, Chore, Recurrence, SystemValues

# set some globals
VERBOSITY = 1
WTF_CSRF_SECRET_KEY = CREDS['WTF_CSRF_SECRET_KEY']

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    flash('Error: There was a problem with your request', category='danger')
    _log.log('400 error encountered. URL: {0}, IP: {1}'.format(request.url, request.remote_addr), LogType.ERROR)
    return render_template('error.html', title='Error 400 - Bad request'), 400

@app.errorhandler(404)
def page_not_found(error):
    flash('Error: The file you are trying to access does not exist', category='danger')
    _log.log('404 error encountered. {0}, IP: {1}'.format(request.url, request.remote_addr), LogType.ERROR)
    return render_template('error.html', title='Error 404 - File not found'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Error: The server encountered an internal error', category='danger')
    _log.log('500 error encountered. {0}, IP: {1}'.format(request.url, request.remote_addr), LogType.ERROR)
    return render_template('error.html', title='Error 500 - Internal server error'), 500

def log_path():
    _log.log('Path: {0}'.format(request.path), LogType.INFO)


# Forms

# Cross site protection
csrf = CSRFProtect()
csrf.init_app(app)

# User Add Form
class UserAddForm(FlaskForm):
    username = TextField('Username:', validators=[validators.required()])
    password = PasswordField('Password:', validators=[validators.required()])
    email_address = TextField('Email:', validators=[validators.required()])
    first_name = TextField('First Name:', validators=[validators.required()])
    middle_name = TextField('Middle Name:', validators=[validators.optional()])
    last_name = TextField('Last Name:', validators=[validators.optional()])
    date_of_birth = DateField(
        'Birth date:', format='%Y-%m-%d', validators=[validators.required()])

# Chore Add Form
class ChoreAddForm(FlaskForm):
    name = TextField('Chore Name:', validators=[validators.required()])
    description = TextField('Description:', validators=[validators.required()])
    due_date = DateField('Due Date:', format='%Y-%m-%d',
                         validators=[validators.optional()])
    points = IntegerField('Points:', validators=[validators.required()])
    assigned_to = SelectField('Assign To:', coerce=int, validators=[validators.optional()])
    recurrence_id = SelectField('Recurrence:', coerce=int, validators=[validators.optional()])

# Chore Edit Form
class ChoreEditForm(FlaskForm):
    name = TextField('Chore Name:', validators=[validators.required()])
    description = TextField('Description:', validators=[validators.required()])
    due_date = DateField('Due Date:', format='%Y-%m-%d',
                         validators=[validators.optional()])
    points = IntegerField('Points:', validators=[validators.required()])
    assigned_to = SelectField('Assign To:', coerce=int, validators=[validators.optional()])
    recurrence_id = SelectField('Recurrence:', coerce=int, validators=[validators.optional()])

# Chore Reassign Form
class ChoreReassignForm(FlaskForm):
    reassign_to = SelectField('Reassign to:', coerce=int, validators=[validators.optional()])

# Password Reset Form
class PasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password:', validators=[validators.required()])
    new_password_verify = PasswordField('Verify New Password:', validators=[validators.required()])

# Reward Add Form
class RewardAddForm(FlaskForm):
    name = TextField('Reward Name:', validators=[validators.required()])
    description = TextField('Description:', validators=[validators.required()])
    points = IntegerField('Points:', validators=[validators.required()])

# Reward Edit Form
class RewardEditForm(FlaskForm):
    name = TextField('Reward Name:', validators=[validators.required()])
    description = TextField('Description:', validators=[validators.required()])
    points = IntegerField('Points:', validators=[validators.required()])

# User Edit Admin Form Other
class UserEditOtherAdminForm(FlaskForm):
    username = TextField('Username:', validators=[validators.required()])
    new_password = PasswordField('New Password:', validators=[validators.optional()])
    new_password_verify = PasswordField('Verify New Password:', validators=[validators.optional()])
    email_address = TextField('Email:', validators=[validators.required()])
    first_name = TextField('First Name:', validators=[validators.required()])
    middle_name = TextField('Middle Name:', validators=[validators.optional()])
    last_name = TextField('Last Name:', validators=[validators.optional()])
    date_of_birth = DateField(
        'Birth date:', format='%Y-%m-%d', validators=[validators.required()])
    role_id = SelectField("Role:", coerce=int, validators=[validators.required()])

# User Edit Form Self
class UserEditSelfForm(FlaskForm):
    username = TextField('Username:', validators=[validators.required()])
    old_password = PasswordField('Old Password:', validators=[validators.optional()])
    new_password = PasswordField('New Password:', validators=[validators.optional()])
    new_password_verify = PasswordField('Verify New Password:', validators=[validators.optional()])
    email_address = TextField('Email:', validators=[validators.required()])
    first_name = TextField('First Name:', validators=[validators.required()])
    middle_name = TextField('Middle Name:', validators=[validators.optional()])
    last_name = TextField('Last Name:', validators=[validators.optional()])
    date_of_birth = DateField(
        'Birth date:', format='%Y-%m-%d', validators=[validators.required()])

# User Edit Admin Form Self
class UserEditSelfAdminForm(UserEditSelfForm):
    role_id = SelectField("Role:", coerce=int, validators=[validators.required()])

# User Login Form
class UserLoginForm(FlaskForm):
    username = TextField('Username:', validators=[validators.required()])
    password = PasswordField('Password:', validators=[validators.required()])


# Jinja context processors
@app.context_processor
def is_admin():
    """ Determine if a user is admin """
    if 'logged_in' in session:
        if session['role_id'] == app.config['ADMIN_ROLE_ID']:
            return dict(is_admin=True)

    return dict(is_admin=False)

@app.context_processor
def admin_role_id():
    """ Return the admin role id """
    return dict(admin_role_id=app.config['ADMIN_ROLE_ID'])

@app.context_processor
def application_version():
    """ Return the application version number """
    return dict(application_version=app.config['APPLICATION_VERSION'])

@app.context_processor
def role_utility():
    """ Return the name of a role given its id"""
    def role_name(role_id):
        role = Role.Role.GetById(role_id)
        if role:
            return role.name
        else:
            return 'No role found matching that id'
            
    return dict(role_name=role_name)

@app.context_processor
def user_utility():
    """ Return the full name of a user given his/her id"""
    def user_full_name(user_id):
        user = User.User.GetById(user_id)
        if user:
            return user.full_name
        return 'unassigned'
            
    return dict(user_full_name=user_full_name)

@app.context_processor
def chore_utility():

    def chore_recurrence_name(recurrence_id):
        recurrence = Recurrence.Recurrence.GetById(recurrence_id)
        return recurrence.frequency_name

    return dict(chore_recurrence_name=chore_recurrence_name)

# Route decorators

def login_required(f):
    """ Ensure the user is logged in, send to login if not"""
    """Things to do to check and make sure a user is logged in
       1. check if session has a logged_in key, if not, send to splash page
       2. compare the current time to the last logged_in timestamp
          if the difference is greater than the timeout, send back to the login page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        _log.log('login check', LogType.INFO)
        # check to see if we're logged in
        if 'logged_in' not in session:
            return splash()
        else:
            # get the current time and see if it's more than the timeout greater
            #   than the last time a logged_in timestamp was stored
            #   if it's not store a new logged_in timestamp
            if 'timeout' in session:
                now = config.get_now()
                delta = session['timeout'] * 60
                if now - session['logged_in'] > delta:
                    _log.log('session timed out', LogType.INFO)
                    session.clear()
                    return redirect(url_for('user_login'))
                else:
                    session['logged_in'] = now
            else:
                session['timeout'] = 10
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """ Ensures the user is admin, and forwards to the index if not """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        _log.log('admin check', LogType.INFO)
        if session['role_id'] == app.config['ADMIN_ROLE_ID']:
            _log.log('user is admin', LogType.INFO)
            return f(*args, **kwargs)
        else:
            _log.log('attempt by a non-admin to access an admin page', LogType.WARN)
            flash('Error: You must be an administrator to access this page', category='danger')
            return index()
    return decorated_function


# Routes

# Default route
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    log_path()
    user = User.User.GetById(session['user_id'])
    
    if user.role_id == app.config['ADMIN_ROLE_ID']:
        chores = Chore.Chore.GetAll()
    else:
        chores = Chore.Chore.GetByUser(user, False)
    
    return render_template('index.html', title='Dashboard', chores=chores, user=user, now=datetime.now().date())

# Splash page
@app.route('/splash', methods=['GET'])
def splash():
    log_path()
    form = UserLoginForm()
    return render_template('splash.html', form=form, title='Welcome to Chore Explore')

# Admin Routes

# Admin functions route
@app.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin():
    log_path()
    return render_template('admin.html', title='Administrative Actions')

# admin notifications toggle
@app.route('/admin/notifications/toggle/<string:setting>', methods=['GET'])
@login_required
@admin_required
def admin_notifications_toggle(setting=None):
    log_path()
    notifications_setting = (SystemValues.SystemValues.GetById(app.config['SYSTEM_VALUES_NOTIFICATIONS']))

    if(setting.lower() == 'on'):
        # Turn on
        notifications_setting.value_bool = True
        notifications_setting.UpdateData()
        flash('Success: Notifications have been turned on', category='success')
    elif(setting.lower() == 'off'):
        # Turn off
        notifications_setting.value_bool = False
        notifications_setting.UpdateData()
        flash('Success: Notifications have been turned off', category='success')
    else:
        # Invalid
        flash('Error: You did not choose a valid notification setting', category='danger')

    return render_template('admin.html', title='Administrative Actions')


# User routes

# user default
@app.route('/user', methods=['GET'])
@login_required
@admin_required
def user():
    log_path()
    users = User.User.GetAll()
    return render_template('user.html', users=users, title='All Users')

# user login
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    log_path()
    if(request.method == 'POST'):

        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])

        result = User.User.GetByUsername(POST_USERNAME)

        if result and result.VerifyPassword(POST_PASSWORD):
            session['logged_in'] = config.get_now() 
            session['user_id'] = result.id
            session['username'] = result.username
            session['role_id'] = result.role_id
            session['timeout'] = 10
            _log.log('logged in', LogType.INFO)
            flash('Success: You are now logged in', category='success')
        else:
            _log.log('bad credentials', LogType.WARN)
            flash('Warning: Username and/or password were incorrect', category='warning')

        return index()
    else:
        form = UserAddForm()
        return render_template('user_login.html', form=form, title='Log in')

# user logout
@app.route('/user/logout', methods=['GET'])
@login_required
def user_logout():
    log_path()
    if session.get('logged_in'):
        session.clear()
        _log.log('user logged out', LogType.INFO)

    return splash()

# user add
@app.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    log_path()
    errors = None

    if request.method == 'GET':
        form = UserAddForm()

    elif request.method == 'POST':
        form = UserAddForm(request.form)

        if form.validate():
            _log.log('form validated', LogType.INFO)
            newUser = User.User()
            form.populate_obj(newUser)

            try:
                newUser.Add()
            except ErrorHandler.ErrorHandler as error:
                flash('Error {0}: {1}'.format(error.status_code, error.message), category='danger')
                return render_template('user_add.html', form=form, errors=errors, title='Add a User')

            _log.log('added user {}'.format(newUser), LogType.INFO)
            flash('Success: User added', category='success')

            return (redirect(url_for('user')))

        else:
            flash('Error: User not added', category='error')
            errors = form.errors

    return render_template('user_add.html', form=form, errors=errors, title='Add a User')


# user remove
@app.route('/user/remove/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def user_remove(user_id=None):
    log_path()
    user = User.User.GetById(user_id)
    if user:
        if user.id == session['user_id']:
            _log.log('user attempt to remove own account', LogType.WARN)
            flash('Error: You may not remove your own account', category='danger')
        else:
            if User.User.Remove(user):
                _log.log('user removed successfully', LogType.INFO)
                flash('Success: User removed', category='success')
            else:
                _log.log('error removing user', LogType.ERROR)
                flash('Error: User not removed', category='danger')
    else:
        _log.log('could not find user', LogType.WARN)
        flash('Warning: Could not find that user', category='warning')
    return redirect(url_for('user'))

# user view
@app.route('/user/view/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def user_view(user_id=None):
    log_path()
    
    user = User.User.GetById(user_id)

    if not user:
        _log.log('could not find user', LogType.WARN)
        flash('Warning: Could not find that user', category='warning')
        return redirect(url_for('user'))

    return render_template('user_view.html', user=user, title='Viewing User: {}'.format(user.username))

# user edit
@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id=None):
    log_path()
    errors=None
    old_user = User.User.GetById(user_id)

    # Check for user editing self (allowed) or admin editing anyone (also allowed)
    if old_user.id == session['user_id'] or session['role_id'] == app.config['ADMIN_ROLE_ID']:
        if request.method == 'GET':
            
            # Admin editing own account
            if(session['role_id'] == app.config['ADMIN_ROLE_ID'] and session['user_id'] == old_user.id):
                _log.log("admin editing own account", LogType.INFO)
                form = UserEditSelfAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list
                form.role_id.default = old_user.role_id
                form.role_id.data = old_user.role_id

            # Admin editing another account
            elif(session['role_id'] == app.config['ADMIN_ROLE_ID'] and session['user_id'] != old_user.id):
                _log.log("admin editing another account", LogType.INFO)
                form = UserEditOtherAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list
                form.role_id.default = old_user.role_id
                form.role_id.data = old_user.role_id

            # User editing own account
            else:
                _log.log("user editing own account", LogType.INFO)
                form = UserEditSelfForm()
                form.old_password.data = None

            form.username.data = old_user.username
            form.new_password.data = None
            form.new_password_verify.data = None
            form.email_address.data = old_user.email_address
            form.first_name.data = old_user.first_name
            form.middle_name.data = old_user.middle_name
            form.last_name.data = old_user.last_name
            form.date_of_birth.data = old_user.date_of_birth

        if request.method == 'POST':
            # Admin editing own account
            if(session['role_id'] == app.config['ADMIN_ROLE_ID'] and session['user_id'] == old_user.id):
                _log.log("admin editing own account", LogType.INFO)
                form = UserEditSelfAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list
                old_password = form.old_password.data

            # Admin editing another user
            elif(session['role_id'] == app.config['ADMIN_ROLE_ID'] and session['user_id'] != old_user.id):
                _log.log("admin editing another account", LogType.INFO)
                form = UserEditOtherAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list

            # Standard user editing own account
            else:
                _log.log("user editing own account", LogType.INFO)
                form = UserEditSelfForm()

                old_password = form.old_password.data
                

            if form.validate():
                _log.log('form validated', LogType.INFO)

                # Run some uniqueness checks before proceeding
                currentUsers = User.User.GetAll()

                if(form.email_address.data != old_user.email_address):
                    _log.log('user attempt to change email address, checking for uniqueness', LogType.INFO)
                    if(any(u.email_address == form.email_address.data for u in currentUsers)):
                        _log.log('user did not enter a unique email address', LogType.ERROR)
                        flash("Error: That email address is already being used by another user", category="danger")
                        return render_template('user_edit.html', form=form, errors=errors, user=old_user, title='Edit User: {}'.format(old_user.username))
                    _log.log('user attempt to change email address is allowed', LogType.INFO)

                if(form.username.data != old_user.username):
                    _log.log('user attempt to change username, checking for uniqueness', LogType.INFO)
                    if(any(u.email_address == form.email_address.data for u in currentUsers)):
                        _log.log('user did not enter a unique email address', LogType.ERROR)
                        flash("Error: That username is already being used by another user", category="danger")
                        return render_template('user_edit.html', form=form, errors=errors, user=old_user, title='Edit User: {}'.format(old_user.username))
                    _log.log('user attempt to change username is allowed', LogType.INFO)
                
                form.populate_obj(old_user)
                new_password = form.new_password.data
                new_password_verify = form.new_password_verify.data
                
                # If user is updating their password
                if(new_password and new_password_verify and old_password):
                    _log.log('user updating password', LogType.INFO)
                    if(old_user.VerifyPassword(old_password)):
                        _log.log('old password verified', LogType.INFO)
                        if(old_user.UpdatePassword(new_password, new_password_verify, old_password)):
                            _log.log('password updated', LogType.INFO)
                        else:
                            _log.log('could not update password', LogType.ERROR)
                            flash("Error: Password not updated, check that your old password was correct, and that your new password is the same in both fields", category="danger")
                            return render_template('user_edit.html', form=form, errors=errors, user=old_user, title='Edit User: {}'.format(old_user.username))
                    else:
                        _log.log('could not verify old password', LogType.WARN)
                        flash("Error: Could not verify your old password", category="danger")
                        return render_template('user_edit.html', form=form, errors=errors, user=old_user, title='Edit User: {}'.format(old_user.username))

                old_user.UpdateData()
                _log.log('edited user: {}'.format(old_user.username), LogType.INFO)

                # Log the user out if they just edited their own account. This is to reset
                # their session, force them to log in with their new password, etc
                if old_user.id == session['user_id']:
                    _log.log('user edited their own account, logging out', LogType.INFO)
                    session.clear()
                    flash('Notice: You edited your own account and must log in again', category='info')
                    return redirect(url_for('splash'))
                else:
                    flash('Success: User edited', category='success')
                    return redirect(url_for('index'))

            else:
                _log.log('form did not validate: {}'.format(form.errors), LogType.WARN)
                flash('Error: User not edited', category='danger')
                errors = form.errors

        return render_template('user_edit.html', form=form, errors=errors, user=old_user, title='Edit User: {}'.format(old_user.username))

    else:
        _log.log('user attempted to edit an account without permission', LogType.WARN)
        flash('Error: You may not edit other user accounts unless you are an administrator', category='danger')
        return redirect(url_for('index'))

# user reset password
@app.route('/user/reset-password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_reset_password(user_id=None):
    log_path()
    user = User.User.GetById(user_id)

    if(request.method == 'GET'):
        form = PasswordResetForm()
        return render_template('user_reset_password.html', form=form, user=user, title='Reset Password for {}'.format(user.username))
    
    if(request.method == 'POST'):
        form = PasswordResetForm()

        new_password = request.form['new_password']
        new_password_verify = request.form['new_password_verify']

        if(new_password == new_password_verify):
            _log.log("passwords match", LogType.INFO)
            if(user):
                _log.log("user found", LogType.INFO)
                if(user.ResetPassword(new_password, new_password_verify)):
                    flash('Success: Password has been updated', category='success')
                    _log.log("password updated", LogType.INFO)
                    return redirect(url_for('user'))
                else:
                    flash('Error: Could not reset password', category='danger')
                    _log.log("error updating password", LogType.ERROR)
                    return render_template('user_reset_password.html', form=form, user=user, title='Reset Password for {}'.format(user.username))
            else:
                _log.log("user does not exist", LogType.WARN)
                flash('Error: That user does not exist', category='danger')
        else:
            flash('Error: The passwords entered did not match', category='danger')
            _log.log("user entered mismatched passwords", LogType.WARN)
            return render_template('user_reset_password.html', form=form, user=user, title='Reset Password for {}'.format(user.username))


# Chore routes

# chore default
@app.route('/chore', methods=['GET'])
@login_required
def chore():
    log_path()
    chores = Chore.Chore.GetAll()

    return render_template('chore.html', chores=chores, title='All Chores', now=datetime.now().date())

# chore add
@app.route('/chore/add', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_add():
    log_path()
    errors = None

    users = User.User.GetAll()
    recurrences = Recurrence.Recurrence.GetAll()

    # Default values
    users_list = [(0, 'unassigned')]

    # Values from DB
    users_list += [(i.id, i.full_name) for i in users]
    recurrences_list = [(i.id, i.frequency_name) for i in recurrences]

    if request.method == 'GET':
        form = ChoreAddForm()
        form.assigned_to.choices = users_list
        form.recurrence_id.choices = recurrences_list

    if request.method == 'POST':
        form = ChoreAddForm(request.form)
        form.assigned_to.choices = users_list
        form.recurrence_id.choices = recurrences_list

        if form.validate():
            _log.log('form validated', LogType.INFO)

            # Check for unassigned
            if form.assigned_to.data != 0:
                assignTo = User.User.GetById(form.assigned_to.data)

                if assignTo:
                    form.assigned_to.data = assignTo.id
                else:
                    _log.log('user was not found, assigning to none', LogType.WARN)
                    flash('Warning: User was not found. Chore is not assigned.', category='warning')
                    form.assigned_to.data = None
            
            else:
                _log.log('user left chore unassigned', LogType.INFO)
                flash('Warning: Chore was left unassigned.', category='warning')
                form.assigned_to.data = None

            newChore = Chore.Chore(form.name.data)
            form.populate_obj(newChore)

            newChore.Add()

            _log.log('added chore: {}'.format(newChore), LogType.INFO)
            flash('Success: Chore added', category='success')

            return (redirect(url_for('chore')))
        
        else:
            _log.log('form has errors: {}'.format(form.errors), LogType.WARN)
            flash('Error: Chore not added', category='danger')
            errors = form.errors

    return render_template('chore_add.html', form=form, errors=errors, title='Add a Chore')

# chore claim
@app.route('/chore/claim/<int:chore_id>', methods=['GET'])
@login_required
def chore_claim(chore_id=None):
    log_path()
    user_id = session['user_id']

    user = User.User.GetById(user_id)
    chore = Chore.Chore.GetById(chore_id)

    if user and chore and chore.assigned_to == None:
        if chore.AssignTo(user):
            _log.log('chore assigned successfully', LogType.INFO)
            flash('Success: Chore claimed', category='success')
        else:
            _log.log('error assigning chore', LogType.ERROR)
            flash('Error: Chore not claimed', category='danger')
    else:
        _log.log('attempt to claim a chore that is already claimed', LogType.WARN)
        flash('Warning: Chore is already claimed', category='warning')

    return redirect(url_for('chore'))


# chore complete
@app.route('/chore/complete/<int:chore_id>', methods=['GET'])
@login_required
def chore_complete(chore_id=None):
    log_path()
    user = User.User.GetById(session['user_id'])
    chore = Chore.Chore.GetById(chore_id)
    _log.log(chore.assigned_to, LogType.INFO)
    if user and chore and chore.assigned_to == user.id:
        if chore.MarkCompleted() and user.AddPoints(chore.points):
                _log.log('chore completed successfully', LogType.INFO)
                flash('Success: Chore completed', category='success')
        else:
            _log.log('error marking chore complete', LogType.ERROR)
            flash('Error: Chore not completed', category='danger')
    else:
        _log.log('user attempt to complete another user\'s chore', LogType.WARN)
        flash('Warning: You cannot complete another user\'s chore', category='warning')
    return redirect(url_for('chore'))

# chore reassign
@app.route('/chore/reassign/<int:chore_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_reassign(chore_id=None):
    log_path()
    errors = None
    
    chore = Chore.Chore.GetById(chore_id)
    users = User.User.GetAll()

    # Add a 'None' value to the list so it can be set as unassigned (claimable).
    users_list = [(0, 'unassigned')]

    # Grab a user_id/full_name tuple for the form
    users_list += [(i.id, i.full_name) for i in users]

    if chore:
        if request.method == 'GET':
            form = ChoreReassignForm()
            form.reassign_to.choices = users_list
            form.reassign_to.default = chore.assigned_to
            form.reassign_to.data = chore.assigned_to

            return render_template('chore_reassign.html', form=form, errors=errors, chore=chore, title='Reassign {}'.format(chore.name))

        elif request.method == 'POST':
            form = ChoreReassignForm(request.form)
            form.reassign_to.choices = users_list

            if form.validate():
                _log.log('form validated', LogType.INFO)

                # check for unassigned
                if form.reassign_to.data != 0:
                    user = User.User.GetById(form.reassign_to.data)

                    if chore.AssignTo(user):
                        _log.log('reassigned chore to: {}'.format(user), LogType.INFO)
                        flash('Success: Chore reassigned', category='success')
                
                else:
                    if chore.Unassign():
                        _log.log('chore unassigned', LogType.INFO)
                        flash('Success: Chore unassigned', category='success')

                return (redirect(url_for('chore_reassign', chore_id=chore.id)))
            
            else:
                _log.log('form has errors: {}'.format(form.errors), LogType.WARN)
                flash('Error: Chore not reassigned', category='danger')
                errors = form.errors

            return render_template('chore_reassign.html', form=form, errors=errors, chore=chore, title='Reassign {}'.format(chore.name))
    
    else:
        _log.log('attempt to reassign a chore that doesn\'t exist', LogType.WARN)
        flash('Warning: Could not find that chore', category='warning')
        return redirect(url_for('chore'))

# chore remove
@app.route('/chore/remove/<int:chore_id>', methods=['GET'])
@login_required
@admin_required
def chore_remove(chore_id=None):
    log_path()
    chore = Chore.Chore.GetById(chore_id)
    if chore:
        if Chore.Chore.Remove(chore):
            _log.log('chore removed successfully', LogType.INFO)
            flash('Success: Chore removed', category='success')
        else:
            _log.log('error removing chore', LogType.ERROR)
            flash('Error: Chore not removed', category='danger')
    else:
        _log.log('error finding chore', LogType.WARN)
        flash('Warning: Could not find that chore', category='warning')
    return redirect(url_for('chore'))

# chore view
@app.route('/chore/view/<int:chore_id>', methods=['GET'])
@login_required
def chore_view(chore_id=None):
    log_path()
    
    chore = Chore.Chore.GetById(chore_id)

    if not chore:
        _log.log('error finding chore', LogType.WARN)
        flash('Warning: Could not find that chore', category='warning')
        return redirect(url_for('chore'))

    _log.log('chore found', LogType.INFO)

    return render_template('chore_view.html', chore=chore, now=datetime.now().date(), title='Viewing Chore: {}'.format(chore.name))


# chore edit
@app.route('/chore/edit/<int:chore_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_edit(chore_id=None):
    log_path()
    errors=None
    old_chore = Chore.Chore.GetById(chore_id)

    users = User.User.GetAll()
    recurrences = Recurrence.Recurrence.GetAll()

    # Add a 'None' value to the list so it can be set as unassigned (claimable).
    users_list = [(0, 'unassigned')]

    # Values from DB
    users_list += [(i.id, i.full_name) for i in users]
    recurrences_list = [(i.id, i.frequency_name) for i in recurrences]

    if request.method == 'GET':
        form = ChoreEditForm()

        form.assigned_to.choices = users_list
        form.recurrence_id.choices = recurrences_list

        form.assigned_to.default = old_chore.assigned_to
        form.recurrence_id.default = old_chore.recurrence_id

        form.name.data = old_chore.name
        form.description.data = old_chore.description
        form.points.data = old_chore.points
        form.due_date.data = old_chore.due_date
        form.recurrence_id.data = old_chore.recurrence_id
        form.assigned_to.data = old_chore.assigned_to

    if request.method == 'POST':
        form = ChoreEditForm(request.form)
        old_chore = Chore.Chore.GetById(chore_id)

        form.assigned_to.choices = users_list
        form.recurrence_id.choices = recurrences_list

        form.assigned_to.default = old_chore.assigned_to
        form.recurrence_id.default = old_chore.recurrence_id

        if form.validate():
            _log.log('form validated', LogType.INFO)

            assignTo = User.User.GetById(form.assigned_to.data)

            if assignTo:
                form.assigned_to.data = assignTo.id
            else:
                form.assigned_to.data = None

            form.populate_obj(old_chore)
            old_chore.UpdateData()

            _log.log('edited chore: {}'.format(old_chore.name), LogType.INFO)
            flash('Success: Chore edited', category='success')

            return (redirect(url_for('chore')))

        else:
            _log.log('form has errors: {}'.format(form.errors), LogType.WARN)
            flash('Error: Chore not added', category='danger')
            errors = form.errors

    return render_template('chore_edit.html', form=form, errors=errors, chore=old_chore, title='Edit Chore: {}'.format(old_chore.name))

# Reward Routes

# reward default
@app.route('/reward', methods=['GET'])
@login_required
def reward():
    log_path()
    rewards = Reward.Reward.GetAll()
    return render_template('reward.html', rewards=rewards, title='All Rewards')

# reward add
@app.route('/reward/add', methods=['GET', 'POST'])
@login_required
@admin_required
def reward_add():
    log_path()
    errors = None

    if request.method == 'GET':
        form = RewardAddForm()

    if request.method == 'POST':
        form = RewardAddForm(request.form)

        if form.validate():
            _log.log('form validated', LogType.INFO)
            newReward = Reward.Reward(form.name.data)
            form.populate_obj(newReward)

            newReward.Add()
            _log.log('reward added: {}'.format(newReward), LogType.INFO)
            flash('Success: Reward added', category='success')

            return (redirect(url_for('reward')))

        else:
            _log.log('form has errors: {}'.format(form.errors), LogType.WARN)
            flash('Error: Reward not added', category='danger')
            errors = form.errors
        
    return render_template('reward_add.html', form=form, errors=errors, title='Add a reward')

# reward claim
@app.route('/reward/claim/<int:reward_id>', methods=['GET'])
@login_required
def reward_claim(reward_id=None):
    log_path()

    reward = Reward.Reward.GetById(reward_id)
    user = User.User.GetById(session['user_id'])

    if reward:
        if Reward.Reward.Claim(reward, user):
            _log.log('claimed reward successfully', LogType.INFO)
            flash('Success: Reward \'{}\' claimed for {} points'.format(reward.name, reward.points), category='success')
        else:
            _log.log('error claiming reward', LogType.WARN)
            flash('Error: Reward not claimed. Do you have enough points?', category='danger')
    else:
        _log.log('error finding reward', LogType.WARN)
        flash('Warning: Could not find that reward', category='warning')
    return redirect(url_for('reward'))

# reward remove 
@app.route('/reward/remove/<int:reward_id>', methods=['GET'])
@login_required
@admin_required
def reward_remove(reward_id=None):
    log_path()
    reward = Reward.Reward.GetById(reward_id)
    if reward:
        if Reward.Reward.Remove(reward):
            _log.log('removed reward successfully', LogType.INFO)
            flash('Success: Reward removed', category='success')
        else:
            _log.log('error removing reward', LogType.ERROR)
            flash('Error: Reward not removed', category='danger')
    else:
        _log.log('error finding reward', LogType.WARN)
        flash('Warning: Could not find that reward', category='warning')
    return redirect(url_for('reward'))

# reward view
@app.route('/reward/view/<int:reward_id>', methods=['GET'])
@login_required
def reward_view(reward_id=None):
    log_path()
    
    reward = Reward.Reward.GetById(reward_id)

    if not reward:
        _log.log('could not find reward', LogType.WARN)
        flash('Warning: Could not find that reward', category='warning')
        return redirect(url_for('reward'))

    _log.log('reward found', LogType.INFO)

    return render_template('reward_view.html', reward=reward, title='Viewing Reward: {}'.format(reward.name))


# reward edit
@app.route('/reward/edit/<int:reward_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reward_edit(reward_id=None):
    log_path()
    errors=None
    old_reward = Reward.Reward.GetById(reward_id)

    if request.method == 'GET':
        form = RewardEditForm()

        form.name.data = old_reward.name
        form.description.data = old_reward.description
        form.points.data = old_reward.points

    if request.method == 'POST':
        form = RewardEditForm(request.form)
        old_reward = Reward.Reward.GetById(reward_id)

        if form.validate():
            _log.log('form validated', LogType.INFO)

            form.populate_obj(old_reward)
            old_reward.UpdateData()

            _log.log('edited reward: {}'.format(old_reward.name), LogType.INFO)
            flash('Success: Reward edited', category='success')

            return (redirect(url_for('reward')))

        else:
            _log.log('form has errors: {}'.format(form.errors), LogType.WARN)
            flash('Error: Reward not added', category='danger')
            errors = form.errors

    return render_template('reward_edit.html', form=form, errors=errors, reward=old_reward, title='Edit Reward: {}'.format(old_reward.name))

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_error)
    app.run(threaded=False)
