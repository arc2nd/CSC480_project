#!/usr/bin/env python

from flask import Flask, render_template, Response, redirect, url_for, request, session, abort, flash, send_from_directory
from wtforms import TextField, PasswordField, IntegerField, StringField, SubmitField, validators
from wtforms.fields.html5 import DateField
from flask_wtf import FlaskForm, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime, timedelta
from Log import _log

import bcrypt, os, sys, traceback

import config

CREDS = config.get_creds('envs.json', crypt=False)
_log(6, 1, CREDS)


# Static files path
app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = CREDS['SQLALCHEMY_TRACK_MODIFICATIONS'] 
app.config['SQLALCHEMY_DATABASE_URI'] = CREDS['SQLALCHEMY_DATABASE_URI'] 

db = SQLAlchemy(app)

# Our models, import here after db has been instantiated
import Chore, Reward, Role, User

# set some globals
VERBOSITY = 1
WTF_CSRF_SECRET_KEY = CREDS['WTF_CSRF_SECRET_KEY'] 


# forms
csrf = CSRFProtect()
csrf.init_app(app)

class UserForm(FlaskForm):
    username = TextField('Username:', validators=[validators.required()])
    password = PasswordField('Password:', validators=[validators.required()])
    email_address = TextField('Email:', validators=[validators.required()])
    first_name = TextField('First Name:', validators=[validators.required()])
    middle_name = TextField('Middle Name:', validators=[validators.required()])
    last_name = TextField('Last Name:', validators=[validators.required()])
    date_of_birth = DateField('Birth date:', format='%Y-%m-%d', validators=[validators.required()])

class ChoreForm(FlaskForm):
    chorename = TextField('Chore Name:', validators=[validators.required()])
    description = TextField('Description:', validators=[validators.required()])
    due_date = DateField('Due Date:', format='%m/%d/%Y', validators=[])
    points = IntegerField('Points:', validators=[])
    assigned_to = TextField('Assigned To:', validators=[])

class LoginForm(FlaskForm):
    username = TextField('Username:', validators=[validators.required()])
    password = PasswordField('Password:', validators=[validators.required()])


# Route decorators
def login_required(f):
    """Things to do to check and make sure a user is logged in
       1. check if session has a logged_in key, if not, send to login page
       2. compare the current time to the last logged_in timestamp
          if the difference is greater than the timeout, send back to the login page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        _log(1, VERBOSITY, 'login check')
        # check to see if we're logged in 
        if 'logged_in' not in session:
            return redirect(url_for('login_form'))
        else:
            # get the current time and see if it's more than the timeout greater
            #   than the last time a logged_in timestamp was stored
            #   if it's not store a new logged_in timestamp
            if 'timeout' in session:
                now = config.get_now()
                delta = session['timeout'] * 60
                _log(6, VERBOSITY, 'now: {}\ndelta: {}\nelapsedd: {}'.format(now, delta, now - session['logged_in']))
                if now - session['logged_in'] > delta:
                    _log(1, VERBOSITY, 'session timed out')
                    session.clear()
                    return redirect(url_for('login_form'))
                else:
                    session['logged_in'] = now
            else:
                session['timeout'] = 10
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("admin check")
        if session['role_id'] == 0:
            print("user is admin")
            return f(*args, **kwargs)
        else:
            print("user not admin")
            return redirect(url_for('index'))
    return decorated_function


# Account routes
@app.route('/login', methods=['POST'])
def login_process():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    result = User.User.query.filter_by(username=POST_USERNAME).first()

    if result and result.verify(passwd_to_test=POST_PASSWORD):
        session['logged_in'] = config.get_now() 
        session['role_id'] = result.role_id
        session['timeout'] = 10 #result.timeout
        _log(1, VERBOSITY, 'logged in')
    else:
        _log(1, VERBOSITY, 'bad credentials')

    return index()


@app.route('/login', methods=['GET'])
def login_form():
    form = UserForm()
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
@login_required
def logout():

    if session.get('logged_in'):
        session.clear()
        return render_template('logout.html')
    # not logged in, send them to the index
    return index()


# Static routes
@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('static/css', path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('static/fonts', path)

@app.route('/js/<path:path>')
def send_css(path):
    return send_from_directory('static/js', path)


# Default Route
@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')
#    if not session.get('logged_in'):
#        return login_form()
#    else:
#        return render_template('index.html')

# User routes
@app.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    # create a user example
    # testUser = User.User('test', 'test', 'test', 'test')
    # testUser.role_id = 0

    # print(testUser)

    # db.session.add(testUser)
    # db.session.commit()
    
    # print(testUser.username)
    
    # Get from DB example
    users = User.User.query.all()
    return render_template('users.html', users=users)


@app.route('/user_add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    print("user_add")

    if request.method == "GET":
        form = UserForm()

    if request.method == "POST":
        form = UserForm(request.form)
        print (form.errors)

        if form.validate(): 
            print (form.errors)
            print("form validated")
            newUser = User.User()
            form.populate_obj(newUser)

            newUser.Add()
            print("added user: {}".format(newUser))

            return (redirect(url_for('users')))

        print (form.errors)

    return render_template('user_add.html', form=form)

# Chore routes
@app.route('/chores', methods=['GET'])
@login_required
def chores():
    # create a user example
    # testUser = User.User('test', 'test', 'test', 'test')
    # testUser.role_id = 0

    # print(testUser)

    # db.session.add(testUser)
    # db.session.commit()
    
    # print(testUser.username)
    
    # Get from DB example
    chores = Chore.Chore.query.all()

    return render_template('chores.html', chores=chores)


@app.route('/chore_add', methods=['GET', 'POST'])
@login_required
@admin_required
def chore_add():
    print("chore_add")

    if request.method == "GET":
        form = ChoreForm()

    if request.method == "POST":
        form = ChoreForm(request.form)
        print (form.errors)

        if form.validate():
            print (form.errors)
            print("form validated")
            thisUser = User.User.query.filter_by(username=form.assigned_to.data).first()
            form.assigned_to.data = thisUser.id
            newChore = Chore.Chore(form.chorename.data)
            form.populate_obj(newChore)

            newChore.Add()
            print("added chore: {}".format(newChore))

            return (redirect(url_for('chores')))

        print (form.errors)

    return render_template('chore_add.html', form=form)



if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run()
