#!/usr/bin/env python

from flask import Flask, render_template, Response, redirect, url_for, request, session, abort, flash, send_from_directory
from wtforms import TextField, PasswordField, StringField, SubmitField, SelectField, validators
from wtforms.fields.html5 import DateField, IntegerField
from flask_wtf import FlaskForm, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime, timedelta
from Log import _log

import bcrypt
import os
import sys
import traceback

import config

CREDS = config.get_creds('envs.json', crypt=False)
_log(6, 1, CREDS)


# Static files path
app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = CREDS['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SQLALCHEMY_DATABASE_URI'] = CREDS['SQLALCHEMY_DATABASE_URI']
app.config['ADMIN_ROLE_ID'] = CREDS['ADMIN_ROLE_ID']

db = SQLAlchemy(app)

# Our models, import here after db has been instantiated
import Reward, Role, User, Chore

# set some globals
VERBOSITY = 1
WTF_CSRF_SECRET_KEY = CREDS['WTF_CSRF_SECRET_KEY']


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
    assigned_to = TextField('Assigned To:', validators=[validators.optional()])
    #recurrence = SelectField('Recurrence:', choices = [('once', 'Once'), ('weekly', 'Weekly'), ('daily', 'Daily')])

# Reward Add Form
class RewardAddForm(FlaskForm):
    name = TextField('Reward Name:', validators=[validators.required()])
    description = TextField('Description:', validators=[validators.required()])
    points = IntegerField('Points:', validators=[validators.required()])

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


# Route decorators

# Ensures the user is logged in, or forwards to login form if not
def login_required(f):
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

# Ensures the user is admin, and forwards to the splash if not
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        _log(1, VERBOSITY, 'admin check')
        if session['role_id'] == app.config['ADMIN_ROLE_ID']:
            _log(1, VERBOSITY, 'user is admin')
            return f(*args, **kwargs)
        else:
            _log(1, VERBOSITY, 'attempt by a non-admin to access an admin page')
            flash('Error: You must be an administrator to access this page', category='danger')
            return splash()
    return decorated_function

# Default route

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html', title="Home")

# Splash page
@app.route('/splash', methods=['GET'])
def splash():
    form = UserAddForm()
    return render_template('splash.html', form=form, title="Welcome to Chore Explore!")

# Admin functions route
@app.route('/admin', methods=['GET'])
@login_required
@admin_required
def admin():
    return render_template('admin.html', title="Admin Functions")


# User routes

# user default
@app.route('/user', methods=['GET'])
@login_required
@admin_required
def user():
    users = User.User.GetAll()
    return render_template('user.html', users=users, title="Users")

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
        return render_template('user_login.html', form=form, title="Log in")

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

    if request.method == "GET":
        form = UserAddForm()

    elif request.method == "POST":
        form = UserAddForm(request.form)

        if form.validate():
            _log(1, VERBOSITY, 'form validated')
            newUser = User.User()
            form.populate_obj(newUser)

            User.User.Add(newUser)

            _log(1, VERBOSITY, 'added user {}'.format(newUser))
            flash('Succes: User added', category='success')

            return (redirect(url_for('user')))

        else:
            flash('Error: User not added', category='error')
            errors = form.errors

    return render_template('user_add.html', form=form, errors=errors, title="Add a user")


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
            if user.Remove(user):
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

    return render_template('user_view.html', user=user, title="Viewing {}".format(user.username))

# Chore routes

# chore default
@app.route('/chore', methods=['GET'])
@login_required
def chore():
    chores = Chore.Chore.GetAll()

    return render_template('chore.html', chores=chores, title="Chores")

# chore add
@app.route('/chore/add', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_add():
    _log(1, VERBOSITY, 'chore/add')
    errors = None

    if request.method == "GET":
        form = ChoreAddForm()

    if request.method == "POST":
        form = ChoreAddForm(request.form)
        _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))

        if form.validate():
            _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
            _log(1, VERBOSITY, 'form validated')

            assignTo = User.User.GetByUsername(form.assigned_to.data)

            if assignTo:
                form.assigned_to.data = assignTo.id
            else:
                form.assigned_to.data = None

            newChore = Chore.Chore(form.name.data)
            form.populate_obj(newChore)

            Chore.Chore.Add(newChore)

            _log(1, VERBOSITY, 'added chore: {}'.format(newChore))
            flash('Success: Chore added', category='success')

            return (redirect(url_for('chore')))
        
        else:
            _log(1, VERBOSITY, 'form has errors: {}'.format(form.errors))
            flash('Error: Chore not added', category='danger')
            errors = form.errors

    return render_template('chore_add.html', form=form, errors=errors, title="Add a chore")

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

# chore remove
@app.route('/chore/remove/<int:chore_id>', methods=['GET'])
@login_required
@admin_required
def chore_remove(chore_id=None):
    _log(1, VERBOSITY, 'chore/remove')
    chore = Chore.Chore.GetById(chore_id)
    if chore:
        if chore.Remove(chore):
            _log(1, VERBOSITY, 'chore removed successfully')
            flash('Success: Chore removed', category='success')
        else:
            _log(1, VERBOSITY, 'error removing chore')
            flash('Error: Chore not removed', category='danger')
    else:
        _log(1, VERBOSITY, 'error finding chore')
        flash('Warning: Could not find that chore', category='warning')
    return redirect(url_for('chore'))


# Reward Routes

# reward default
@app.route('/reward', methods=['GET'])
@login_required
def reward():
    _log(1, VERBOSITY, 'reward/')
    rewards = Reward.Reward.GetAll()
    return render_template('reward.html', rewards=rewards, title="Rewards")

# reward add
@app.route('/reward/add', methods=['GET', 'POST'])
@login_required
@admin_required
def reward_add():
    _log(1, VERBOSITY, 'reward/add')
    errors = None

    if request.method == "GET":
        form = RewardAddForm()

    if request.method == "POST":
        form = RewardAddForm(request.form)
        _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))

        if form.validate():
            _log(1, VERBOSITY, 'form errors: {}'.format(form.errors))
            _log(1, VERBOSITY, 'form validated')
            newReward = Reward.Reward(form.name.data)
            form.populate_obj(newReward)

            Reward.Reward.Add(newReward)
            _log(1, VERBOSITY, 'reward added: {}'.format(newReward))
            flash('Success: Reward added', category='success')

            return (redirect(url_for('reward')))

        else:
            _log(1, VERBOSITY, 'error adding reward: {}'.format(form.errors))
            flash('Error: Reward not added', category='danger')
            errors = form.errors
        
    return render_template('reward_add.html', form=form, errors=errors)


# reward remove 
@app.route('/reward/remove/<int:reward_id>', methods=['GET'])
@login_required
@admin_required
def reward_remove(reward_id=None):
    _log(1, VERBOSITY, 'reward/remove')
    reward = Reward.Reward.GetById(reward_id)
    if reward:
        if reward.Remove(reward):
            _log(1, VERBOSITY, 'removed reward successfully')
            flash('Success: Reward removed', category='success')
        else:
            _log(1, VERBOSITY, 'error removing reward')
            flash('Error: Reward not removed', category='danger')
    else:
        _log(1, VERBOSITY, 'error finding reward')
        flash('Warning: Could not find that reward', category='warning')
    return redirect(url_for('reward'))


# Test Routes

@app.route('/test/chore', methods=['GET'])
def test_chore():
    # Chore tests

    # Constructor
    chore = Chore.Chore("test1")

    # Assignments
    chore.description = "test1"
    chore.points = 1

    # Create
    Chore.Chore.Add(chore)

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
    user.username = "test4"
    user.points = 1
    user.password = "testpassword"
    user.email_address = "test4@email.address"
    user.first_name = "test"
    user.date_of_birth = '1945-02-02'

    # Create
    User.User.Add(user)

    # Read
    singleUserById = User.User.GetById(user.id)
    singleUserByUsername = User.User.GetByUsername(user.username)
    allUsers = User.User.GetAll()

    # Update
    updatedSuccessfully = singleUserById.UpdatePassword("newpass", "newpass", "testpassword")

    # Utility
    isPasswordCorrect = singleUserById.VerifyPassword("newpass")
    password = User.User.EncryptPassword("encryptThis")

    # Delete
    User.User.Remove(user)

    return redirect(url_for('index'))

@app.route('/test/reward', methods=['GET'])
def test_reward():
    # Reward tests

    # Constructor
    reward = Reward.Reward("test1")

    # Assignments
    reward.name = "test"
    reward.description = "test1"
    reward.points = 1

    # Create
    Reward.Reward.Add(reward)

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
    role = Role.Role("test1")

    # Assignments
    role.name = "test"

    # Create
    Role.Role.Add(role)

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
    app.run()
