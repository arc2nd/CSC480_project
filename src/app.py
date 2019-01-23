#!/usr/bin/env python

from flask import Flask, render_template, Response, redirect, url_for, request, session, abort, flash, send_from_directory, jsonify
from wtforms import TextField, PasswordField, StringField, SubmitField, SelectField, validators
from wtforms.fields.html5 import DateField, IntegerField
from flask_wtf import FlaskForm, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime, timedelta
from Log import _log
import ErrorHandler

import bcrypt
import os
import sys
import traceback

import config

CREDS = config.get_creds('envs.json', crypt=False)
_log(6, 1, CREDS)

# Static files path
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = CREDS['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SQLALCHEMY_DATABASE_URI'] = CREDS['SQLALCHEMY_DATABASE_URI']
app.config['ADMIN_ROLE_ID'] = CREDS['ADMIN_ROLE_ID']
app.config['STANDARD_ROLE_ID'] = CREDS['STANDARD_ROLE_ID']
app.config['APPLICATION_VERSION'] = CREDS['APPLICATION_VERSION']

db = SQLAlchemy(app)

# Our models, import here after db has been instantiated
import Reward, Role, User, Chore, Recurrence

# set some globals
VERBOSITY = 1
WTF_CSRF_SECRET_KEY = CREDS['WTF_CSRF_SECRET_KEY']

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    flash('Error: There was a problem with your request', category='danger')
    return render_template('error.html', title='Error 400'), 400

@app.errorhandler(404)
def page_not_found(error):
    flash('Error: The file you are trying to access does not exist', category='danger')
    return render_template('error.html', title='Error 404'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Error: The server encountered an internal error', category='danger')
    return render_template('error.html', title='Error 500'), 500

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
        return 'Unassigned'
            
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
        _log(1, VERBOSITY, 'login check')
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
                _log(6, VERBOSITY, 'now: {}\ndelta: {}\nelapsed: {}'.format(
                    now, delta, now - session['logged_in']))
                if now - session['logged_in'] > delta:
                    _log(1, VERBOSITY, 'session timed out')
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
        _log(1, VERBOSITY, 'admin check')
        if session['role_id'] == app.config['ADMIN_ROLE_ID']:
            _log(1, VERBOSITY, 'user is admin')
            return f(*args, **kwargs)
        else:
            _log(1, VERBOSITY, 'attempt by a non-admin to access an admin page')
            flash('Error: You must be an administrator to access this page', category='danger')
            return index()
    return decorated_function


# Routes

# Default route
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    user = User.User.GetById(session['user_id'])
    
    if user.role_id == app.config['ADMIN_ROLE_ID']:
        chores = Chore.Chore.GetAll()
    else:
        chores = Chore.Chore.GetByUser(user, False)
    
    return render_template('index.html', title='Dashboard', chores=chores, user=user)

# Splash page
@app.route('/splash', methods=['GET'])
def splash():
    form = UserAddForm()
    return render_template('splash.html', form=form, title='Welcome to Chore Explore')

# Admin functions route
@app.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin():
    return render_template('admin.html', title='Administrative Actions')


# User routes

# user default
@app.route('/user', methods=['GET'])
@login_required
@admin_required
def user():
    users = User.User.GetAll()
    return render_template('user.html', users=users, title='All Users')

# user login
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
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
            _log(1, VERBOSITY, 'logged in')
            flash('Success: You are now logged in', category='success')
        else:
            _log(1, VERBOSITY, 'bad credentials')
            flash('Warning: Username and/or password were incorrect', category='warning')

        return index()
    else:
        form = UserAddForm()
        return render_template('user_login.html', form=form, title='Log in')

# user logout
@app.route('/user/logout', methods=['GET'])
@login_required
def user_logout():
    if session.get('logged_in'):
        session.clear()
        _log(1, VERBOSITY, 'user logged out')

    return splash()

# user add
@app.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    _log(1, VERBOSITY, 'user/add')
    errors = None

    if request.method == 'GET':
        form = UserAddForm()

    elif request.method == 'POST':
        form = UserAddForm(request.form)

        if form.validate():
            _log(1, VERBOSITY, 'form validated')
            newUser = User.User()
            form.populate_obj(newUser)

            try:
                newUser.Add()
            except ErrorHandler.ErrorHandler as error:
                flash('Error {0}: {1}'.format(error.status_code, error.message), category='danger')
                return render_template('error.html', title='Error {}'.format(error.status_code))

            _log(1, VERBOSITY, 'added user {}'.format(newUser))
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
    user = User.User.GetById(user_id)
    if user:
        if user.id == session['user_id']:
            _log(1, VERBOSITY, 'user attempt to remove own account')
            flash('Error: You may not remove your own account', category='danger')
        else:
            if User.User.Remove(user):
                _log(1, VERBOSITY, 'user removed successfully')
                flash('Success: User removed', category='success')
            else:
                _log(1, VERBOSITY, 'error removing user')
                flash('Error: User not removed', category='danger')
    else:
        _log(1, VERBOSITY, 'error finding user')
        flash('Warning: Could not find that user', category='danger')
    return redirect(url_for('user'))

# user view
@app.route('/user/view/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def user_view(user_id=None):
    _log(1, VERBOSITY, 'user/view')
    
    user = User.User.GetById(user_id)

    if not user:
        _log(1, VERBOSITY, 'error finding user')
        flash('Warning: Could not find that user', category='danger')
        return redirect(url_for('user'))

    _log(1, VERBOSITY, 'user found')

    return render_template('user_view.html', user=user, title='Viewing User: {}'.format(user.username))

# user edit
@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id=None):
    errors=None
    old_user = User.User.GetById(user_id)

    # Check for user editing self (allowed) or admin editing anyone (also allowed)
    if old_user.id == session['user_id'] or session['role_id'] == app.config['ADMIN_ROLE_ID']:
        if request.method == 'GET':
            
            # Admin editing own account
            if(session['role_id'] == app.config['ADMIN_ROLE_ID'] and session['user_id'] == old_user.id):
                form = UserEditSelfAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list
                form.role_id.default = old_user.role_id
                form.role_id.data = old_user.role_id

            # Admin editing another account
            elif(session['role_id'] == app.config['ADMIN_ROLE_ID'] and session['user_id'] != old_user.id):
                form = UserEditOtherAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list
                form.role_id.default = old_user.role_id
                form.role_id.data = old_user.role_id

            # User editing own account
            else:
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
                form = UserEditSelfAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list
                old_password = form.old_password.data

            # Admin editing another user
            elif(session['role_id'] == app.config['ADMIN_ROLE_ID'] and session['user_id'] != old_user.id):
                form = UserEditOtherAdminForm()

                roles = Role.Role.GetAll()
                roles_list = [(i.id, i.name) for i in roles]
                form.role_id.choices = roles_list

            # Standard user editing own account
            else:
                form = UserEditSelfForm()

                old_password = form.old_password.data
                

            if form.validate():
                _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
                _log(1, VERBOSITY, 'form validated')

                form.populate_obj(old_user)

                new_password = form.new_password.data
                new_password_verify = form.new_password_verify.data
                
                # If user is updating their password
                if(new_password and new_password_verify and old_password):
                    _log(1, VERBOSITY, 'user updating password')
                    if(old_user.VerifyPassword(old_password)):
                        _log(1, VERBOSITY, 'old password verified')
                        if(old_user.UpdatePassword(new_password, new_password_verify, old_password)):
                            _log(1, VERBOSITY, 'password updated')
                        else:
                            _log(1, VERBOSITY, 'could not update password')
                            flash("Error: Password not updated, check that your old password was correct, and that your new password is the same in both fields", category="danger")
                            return render_template('user_edit.html', form=form, errors=errors, user=old_user, title='Edit User: {}'.format(old_user.username))
                    else:
                        _log(1, VERBOSITY, 'could not verify old password')
                        flash("Error: Could not verify your old password", category="danger")

                # Not updating password, just update the other data
                else:
                    old_user.UpdateData()

                _log(1, VERBOSITY, 'edited user: {}'.format(old_user.username))

                # Log the user out if they just edited their own account. This is to reset
                # their session, force them to log in with their new password, etc
                if old_user.id == session['user_id']:
                    _log(1, VERBOSITY, 'user edited their own account, logging out')
                    session.clear()
                    flash('Notice: You edited your own account and must log in again', category='info')
                    return redirect(url_for('splash'))
                else:
                    flash('Success: User edited', category='success')
                    return redirect(url_for('index'))

            else:
                _log(1, VERBOSITY, 'form has errors: {}'.format(form.errors))
                flash('Error: User not edited', category='danger')
                errors = form.errors

        return render_template('user_edit.html', form=form, errors=errors, user=old_user, title='Edit User: {}'.format(old_user.username))

    else:
        _log(1, VERBOSITY, 'user attempted to edit an account without permission')
        flash('Error: You may not edit other user accounts unless you are an administrator', category='danger')
        return redirect(url_for('index'))

# user reset password
@app.route('/user/reset-password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_reset_password(user_id=None):

    user = User.User.GetById(user_id)

    if(request.method == 'GET'):
        form = PasswordResetForm()
        return render_template('user_reset_password.html', form=form, user=user, title='Reset Password for {}'.format(user.username))
    
    if(request.method == 'POST'):
        form = PasswordResetForm()

        new_password = request.form['new_password']
        new_password_verify = request.form['new_password_verify']

        if(new_password == new_password_verify):
            if(user):
                if(user.ResetPassword(new_password, new_password_verify)):
                    flash('Success: Password has been updated', category='success')
                    return redirect(url_for('user'))
                else:
                    flash('Error: Could not reset password', category='danger')
                    return render_template('user_reset_password.html', form=form, user=user, title='Reset Password for {}'.format(user.username))
            else:
                flash('Error: That user does not exist', category='danger')
        else:
            flash('Error: The passwords entered did not match', category='danger')
            return render_template('user_reset_password.html', form=form, user=user, title='Reset Password for {}'.format(user.username))


# Chore routes

# chore default
@app.route('/chore', methods=['GET'])
@login_required
def chore():
    chores = Chore.Chore.GetAll()

    return render_template('chore.html', chores=chores, title='All Chores')

# chore add
@app.route('/chore/add', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_add():
    _log(1, VERBOSITY, 'chore/add')
    errors = None

    users = User.User.GetAll()
    recurrences = Recurrence.Recurrence.GetAll()

    # Default values
    users_list = [(0, 'Unassigned')]

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

        _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))

        if form.validate():
            _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
            _log(1, VERBOSITY, 'form validated')

            # Check for unassigned
            if form.assigned_to.data != 0:
                assignTo = User.User.GetById(form.assigned_to.data)

                if assignTo:
                    form.assigned_to.data = assignTo.id
                else:
                    _log(1, VERBOSITY, 'user was not found, assigning to none')
                    flash('Warning: User was not found. Chore is not assigned.', category='warning')
                    form.assigned_to.data = None
            
            else:
                _log(1, VERBOSITY, 'user left chore unassigned')
                flash('Warning: Chore was left unassigned.', category='warning')
                form.assigned_to.data = None

            newChore = Chore.Chore(form.name.data)
            form.populate_obj(newChore)

            newChore.Add()

            _log(1, VERBOSITY, 'added chore: {}'.format(newChore))
            flash('Success: Chore added', category='success')

            return (redirect(url_for('chore')))
        
        else:
            _log(1, VERBOSITY, 'form has errors: {}'.format(form.errors))
            flash('Error: Chore not added', category='danger')
            errors = form.errors

    return render_template('chore_add.html', form=form, errors=errors, title='Add a Chore')

# chore claim
@app.route('/chore/claim/<int:chore_id>', methods=['GET'])
@login_required
def chore_claim(chore_id=None):
    _log(1, VERBOSITY, 'chore/claim')

    user_id = session['user_id']

    user = User.User.GetById(user_id)
    chore = Chore.Chore.GetById(chore_id)

    if user and chore and chore.assigned_to == None:
        if chore.AssignTo(user):
            _log(1, VERBOSITY, 'chore assigned successfully')
            flash('Success: Chore claimed', category='success')
        else:
            _log(1, VERBOSITY, 'error assigning chore')
            flash('Error: Chore not claimed', category='danger')
    else:
        _log(1, VERBOSITY, 'chore already claimed')
        flash('Warning: Chore is already claimed', category='warning')

    return redirect(url_for('chore'))


# chore complete
@app.route('/chore/complete/<int:chore_id>', methods=['GET'])
@login_required
def chore_complete(chore_id=None):
    _log(1, VERBOSITY, 'chore/complete')
    user = User.User.GetById(session['user_id'])
    chore = Chore.Chore.GetById(chore_id)
    _log(1, VERBOSITY, chore.assigned_to)
    if user and chore and chore.assigned_to == user.id:
        if chore.MarkCompleted() and user.AddPoints(chore.points):
                _log(1, VERBOSITY, 'chore completed successfully')
                flash('Success: Chore completed', category='success')
        else:
            _log(1, VERBOSITY, 'error marking chore complete')
            flash('Error: Chore not completed', category='danger')
    else:
        _log(1, VERBOSITY, 'user attempt to complete another user\'s chore')
        flash('Warning: You cannot complete another user\'s chore', category='warning')
    return redirect(url_for('chore'))

# chore reassign
@app.route('/chore/reassign/<int:chore_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_reassign(chore_id=None):
    _log(1, VERBOSITY, 'chore/reassign')
    errors = None
    
    chore = Chore.Chore.GetById(chore_id)
    users = User.User.GetAll()

    # Add a 'None' value to the list so it can be set as unassigned (claimable).
    users_list = [(0, 'Unassigned')]

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
                _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
                _log(1, VERBOSITY, 'form validated')

                # check for unassigned
                if form.reassign_to.data != 0:
                    user = User.User.GetById(form.reassign_to.data)

                    if chore.AssignTo(user):
                        _log(1, VERBOSITY, 'reassigned chore to: {}'.format(user))
                        flash('Success: Chore reassigned', category='success')
                
                else:
                    if chore.Unassign():
                        _log(1, VERBOSITY, 'chore unassigned')
                        flash('Success: Chore unassigned', category='success')

                return (redirect(url_for('chore_reassign', chore_id=chore.id)))
            
            else:
                _log(1, VERBOSITY, 'form has errors: {}'.format(form.errors))
                flash('Error: Chore not reassigned', category='danger')
                errors = form.errors

            return render_template('chore_reassign.html', form=form, errors=errors, chore=chore, title='Reassign {}'.format(chore.name))
    
    else:
        _log(1, VERBOSITY, 'attempt to reassign a chore that doesn\'t exist')
        flash('Warning: Could not find that chore', category='warning')
        return redirect(url_for('chore'))

# chore remove
@app.route('/chore/remove/<int:chore_id>', methods=['GET'])
@login_required
@admin_required
def chore_remove(chore_id=None):
    _log(1, VERBOSITY, 'chore/remove')
    chore = Chore.Chore.GetById(chore_id)
    if chore:
        if Chore.Chore.Remove(chore):
            _log(1, VERBOSITY, 'chore removed successfully')
            flash('Success: Chore removed', category='success')
        else:
            _log(1, VERBOSITY, 'error removing chore')
            flash('Error: Chore not removed', category='danger')
    else:
        _log(1, VERBOSITY, 'error finding chore')
        flash('Warning: Could not find that chore', category='warning')
    return redirect(url_for('chore'))

# chore view
@app.route('/chore/view/<int:chore_id>', methods=['GET'])
@login_required
@admin_required
def chore_view(chore_id=None):
    _log(1, VERBOSITY, 'chore/view')
    
    chore = Chore.Chore.GetById(chore_id)

    if not chore:
        _log(1, VERBOSITY, 'error finding chore')
        flash('Warning: Could not find that chore', category='danger')
        return redirect(url_for('chore'))

    _log(1, VERBOSITY, 'chore found')

    return render_template('chore_view.html', chore=chore, title='Viewing Chore: {}'.format(chore.name))


# chore edit
@app.route('/chore/edit/<int:chore_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_edit(chore_id=None):
    errors=None
    old_chore = Chore.Chore.GetById(chore_id)

    users = User.User.GetAll()
    recurrences = Recurrence.Recurrence.GetAll()

    # Add a 'None' value to the list so it can be set as unassigned (claimable).
    users_list = [(0, 'Unassigned')]

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
        _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))

        form.assigned_to.choices = users_list
        form.recurrence_id.choices = recurrences_list

        form.assigned_to.default = old_chore.assigned_to
        form.recurrence_id.default = old_chore.recurrence_id

        if form.validate():
            _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
            _log(1, VERBOSITY, 'form validated')

            assignTo = User.User.GetById(form.assigned_to.data)

            if assignTo:
                form.assigned_to.data = assignTo.id
            else:
                form.assigned_to.data = None

            form.populate_obj(old_chore)
            old_chore.UpdateData()

            _log(1, VERBOSITY, 'edited chore: {}'.format(old_chore.name))
            flash('Success: Chore edited', category='success')

            return (redirect(url_for('chore')))

        else:
            _log(1, VERBOSITY, 'form has errors: {}'.format(form.errors))
            flash('Error: Chore not added', category='danger')
            errors = form.errors

    return render_template('chore_edit.html', form=form, errors=errors, chore=old_chore, title='Edit Chore: {}'.format(old_chore.name))

# Reward Routes

# reward default
@app.route('/reward', methods=['GET'])
@login_required
def reward():
    _log(1, VERBOSITY, 'reward/')
    rewards = Reward.Reward.GetAll()
    return render_template('reward.html', rewards=rewards, title='All Rewards')

# reward add
@app.route('/reward/add', methods=['GET', 'POST'])
@login_required
@admin_required
def reward_add():
    _log(1, VERBOSITY, 'reward/add')
    errors = None

    if request.method == 'GET':
        form = RewardAddForm()

    if request.method == 'POST':
        form = RewardAddForm(request.form)
        _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))

        if form.validate():
            _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
            _log(1, VERBOSITY, 'form validated')
            newReward = Reward.Reward(form.name.data)
            form.populate_obj(newReward)

            newReward.Add()
            _log(1, VERBOSITY, 'reward added: {}'.format(newReward))
            flash('Success: Reward added', category='success')

            return (redirect(url_for('reward')))

        else:
            _log(1, VERBOSITY, 'error adding reward: {}'.format(form.errors))
            flash('Error: Reward not added', category='danger')
            errors = form.errors
        
    return render_template('reward_add.html', form=form, errors=errors, title='Add a reward')

# reward claim
@app.route('/reward/claim/<int:reward_id>', methods=['GET'])
@login_required
def reward_claim(reward_id=None):
    _log(1, VERBOSITY, 'reward/claim')

    reward = Reward.Reward.GetById(reward_id)
    user = User.User.GetById(session['user_id'])

    if reward:
        if Reward.Reward.Claim(reward, user):
            _log(1, VERBOSITY, 'claimed reward successfully')
            flash('Success: Reward \'{}\' claimed for {} points'.format(reward.name, reward.points), category='success')
        else:
            _log(1, VERBOSITY, 'error claiming reward')
            flash('Error: Reward not claimed. Do you have enough points?', category='danger')
    else:
        _log(1, VERBOSITY, 'error finding reward')
        flash('Warning: Could not find that reward', category='warning')
    return redirect(url_for('reward'))

# reward remove 
@app.route('/reward/remove/<int:reward_id>', methods=['GET'])
@login_required
@admin_required
def reward_remove(reward_id=None):
    _log(1, VERBOSITY, 'reward/remove')
    reward = Reward.Reward.GetById(reward_id)
    if reward:
        if Reward.Reward.Remove(reward):
            _log(1, VERBOSITY, 'removed reward successfully')
            flash('Success: Reward removed', category='success')
        else:
            _log(1, VERBOSITY, 'error removing reward')
            flash('Error: Reward not removed', category='danger')
    else:
        _log(1, VERBOSITY, 'error finding reward')
        flash('Warning: Could not find that reward', category='warning')
    return redirect(url_for('reward'))

# reward view
@app.route('/reward/view/<int:reward_id>', methods=['GET'])
@login_required
@admin_required
def reward_view(reward_id=None):
    _log(1, VERBOSITY, 'reward/view')
    
    reward = Reward.Reward.GetById(reward_id)

    if not reward:
        _log(1, VERBOSITY, 'error finding reward')
        flash('Warning: Could not find that reward', category='danger')
        return redirect(url_for('reward'))

    _log(1, VERBOSITY, 'reward found')

    return render_template('reward_view.html', reward=reward, title='Viewing Reward: {}'.format(reward.name))


# reward edit
@app.route('/reward/edit/<int:reward_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reward_edit(reward_id=None):
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
        _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))

        if form.validate():
            _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
            _log(1, VERBOSITY, 'form validated')

            form.populate_obj(old_reward)
            old_reward.UpdateData()

            _log(1, VERBOSITY, 'edited reward: {}'.format(old_reward.name))
            flash('Success: Reward edited', category='success')

            return (redirect(url_for('reward')))

        else:
            _log(1, VERBOSITY, 'form has errors: {}'.format(form.errors))
            flash('Error: Reward not added', category='danger')
            errors = form.errors

    return render_template('reward_edit.html', form=form, errors=errors, reward=old_reward, title='Edit Reward: {}'.format(old_reward.name))

# Test Routes

@app.route('/test/chore', methods=['GET'])
def test_chore():
    # Chore tests

    # Constructor
    chore = Chore.Chore('test1')

    # Assignments
    chore.description = 'test1'
    chore.points = 1

    # Create
    chore.Add()

    # Read
    singleChore = Chore.Chore.GetById(chore.id)
    allChores = Chore.Chore.GetAll()

    # Update
    user = User.User.GetById(0)

    chore.AssignTo(user)

    # Utility
    checkOverdue = chore.IsOverdue()

    # Delete
    Chore.Chore.Remove(chore)

    return redirect(url_for('index'))

@app.route('/test/user', methods=['GET'])
def test_user():
    # User tests

    # Constructor
    user = User.User()

    # Assignments
    user.username = 'test4'
    user.points = 1
    user.password = 'testpassword'
    user.email_address = 'test4@email.address'
    user.first_name = 'test'
    user.date_of_birth = '1945-02-02'

    # Create
    user.Add()

    # Read
    singleUserById = User.User.GetById(user.id)
    singleUserByUsername = User.User.GetByUsername(user.username)
    allUsers = User.User.GetAll()

    # Update
    updatedSuccessfully = singleUserById.UpdatePassword('newpass', 'newpass', 'testpassword')

    # Utility
    isPasswordCorrect = singleUserById.VerifyPassword('newpass')
    password = User.User.EncryptPassword('encryptThis')

    # Delete
    User.User.Remove(user)

    return redirect(url_for('index'))

@app.route('/test/reward', methods=['GET'])
def test_reward():
    # Reward tests

    # Constructor
    reward = Reward.Reward('test1')

    # Assignments
    reward.name = 'test'
    reward.description = 'test1'
    reward.points = 1

    # Create
    reward.Add()

    # Read
    singleReward = Reward.Reward.GetById(reward.id)
    allRewards = Reward.Reward.GetAll()

    # Update

    # Utility

    # Delete
    Reward.Reward.Remove(reward)

    return redirect(url_for('index'))

@app.route('/test/role', methods=['GET'])
def test_role():
    # Role tests

    # Constructor
    role = Role.Role('test1')

    # Assignments
    role.name = 'test'

    # Create
    role.Add()

    # Read
    singleRole = Role.Role.GetById(role.id)
    allRoles = Role.Role.GetAll()

    # Update

    # Utility

    # Delete
    Role.Role.Remove(role)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_error)
    app.run()
