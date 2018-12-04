#!/usr/bin/env python

import os
import sys
import json
import datetime
import calendar
import commands
from functools import wraps

from flask import Flask, render_template, Response, redirect, url_for, request, session, flash

app = Flask(__name__)

VERBOSITY = 1

def _log(priority, msg):
    if VERBOSITY >= priority:
        print(msg)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        for i in session:
            _log(6, i)
        if 'logged_in' not in session:
            return redirect(url_for('login')) #, next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
#@login_required
def index():
    return render_template('index.html')


#@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=["GET", "POST"])
def login():
    form = forms.EmailPasswordForm()
    if form.validate_on_submit():
        new_login = user.User(name=form.email.data)
        _log(1, form.password.data)
        if new_login.verify(passwd=form.password.data):
            ts = calendar.timegm(datetime.datetime.now().timetuple())
            session['user'] = new_login.to_dict()
            session['logged_in'] = ts
            for i in session:
                _log(6, i)
            return redirect(url_for('index'))
        flash('wrong password')
    return render_template('login.html', form=form, footer='False')


@app.route('/logout', methods=['GET'])
def logout():
    user_name = session['user']['name']
    session.pop('user')
    for i in session:
        _log(6, i)
    return render_template('logout.html', user=user_name)


@app.route('/chores', methods=['GET'])
def chores():
    return render_template('chores.html')


@app.route('/available', methods=['GET'])
def available():
    return render_template('available.html')


@app.route('/new_chore', methods=['GET'])
def new_chore():
    return render_template('new_chore.html')


@app.route('/my_account', methods=['GET'])
def my_account():
    return render_template('my_account.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

