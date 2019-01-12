#!/usr/bin/env python

import os
import sys
import json
import calendar
import datetime
import traceback
from functools import wraps

from flask import Flask, render_template, Response, redirect, url_for, request, session, flash

import db
import User
import Chore
import Reward
import Helpers
from Log import _log

app = Flask(__name__)
app.secret_key = Helpers.get_creds('envs.json')['SECRET_KEY']


# set some globals
VERBOSITY = 1
CHORE_CONN = db.CHORE_CONN
USER_CONN = db.USER_CONN
REWARD_CONN = db.REWARD_CONN

def login_required(f):
    """Things to do to check and make sure a user is logged in
       1. check if session has a logged_in key, if not, send to login page
       2. compare the current time to the last logged_in timestamp
          if the difference is greater than the timeout, send back to the login page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # show me what's being stored in session
        for i in session:
            _log(1, VERBOSITY, 'session: {} :: {}'.format(i, session[i]))
        # check to see if we're logged in 
        if 'logged_in' not in session:
            return redirect(url_for('login_form')) #, next=request.url))
        else:
            # get the current time and see if it's more than the timeout greater
            #   than the last time a logged_in timestamp was stored
            #   if it's not store a new logged_in timestamp
            now = Helpers.get_now()
            _log(1, VERBOSITY, 'now: {}'.format(now))
            if 'timeout' in session:
                delta = session['timeout'] * 60
                if now - session['logged_in'] > delta:
                    session.clear()
                    return redirect(url_for('login_form'))
                else:
                    session['logged_in'] = now
            else:
                session['timeout'] = 10
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Check if the user is an admin user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['role'].lower() == 'admin':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return decorated_function



# The actual website endpoints

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
def index():
    is_admin = True if session['role'] == 'admin' else False
    user_list = db.get_all_users(conn=USER_CONN)
    user_dict = {}
    for user in user_list:
        u_dict = db.get_user(conn=USER_CONN, name=user)
        user_dict[user] = u_dict.data_dict
    return render_template('index.html', data={'users': user_dict}, admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        res = request.form
        t_dict = {}
        for i in res:
            t_dict[i] = res[i]
        if Helpers.verify_user(t_dict['username']):
            u = db.get_user(conn=USER_CONN, name=res['username'])
            if u.verify(passwd=res['password']):
                now = Helpers.get_now() 
                session['user'] = u.get_attr(attr='name')
                session['logged_in'] = now
                session['role'] = u.get_attr(attr='role') if u.attr_exists(attr='role') else 'standard'
                session['timeout'] = u.get_attr(attr='timeout') if u.attr_exists(attr='timeout') else 1
                #for i in session:
                #    print('{} :: {}'.format(i, session[i]))
                return redirect(url_for('index'))
    except:
        print(sys.exc_info())
        traceback.print_tb(sys.exc_info()[-1])
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_name = session['user']
    for i in session:
        print('{} :: {}'.format(i, session[i]))
    session.clear()
    return render_template('logout.html', user=user_name)
    return render_template('logout.html')


@app.route('/chores', methods=['GET', 'POST'])
@app.route('/chores/<user>', methods=['GET', 'POST'])
@login_required
def chores(user=None):
    is_admin = True if session['role'] == 'admin' else False
    if user:
        user_chores = db.get_user_chores(CHORE_CONN, user)
        chores_dict = {}
        for c in user_chores:
            chores_dict[c] = db.get_chore(CHORE_CONN, c).data_dict
    return render_template('chores.html', data=chores_dict, admin=is_admin)

@app.route('/new_chore', methods=['GET'])
@login_required
def new_chore():
    is_admin = True if session['role'] == 'admin' else False
    return render_template('new_chore.html', admin=is_admin)


@app.route('/new_chore_results', methods=['GET', 'POST'])
@login_required
def new_chore_results():
    is_admin = True if session['role'] == 'admin' else False
    # general processing of the form we've received
    res = request.form
    if 'cancel' in res:  # check to see if the cancel button has been pressed
        return redirect(url_for('index'))
    _log(1, VERBOSITY, res)
    processed_res, missing = Helpers.process_chore_form(res)  # process the form results and validate
    _log(6, VERBOSITY, missing)
    if len(missing) > 0:
        return render_template('error.html', data=missing)

    # build a chore object, populate it, and stick it in the db
    this_chore = Chore.Chore(processed_res)
    db.write_chore_to_storage(CHORE_CONN, this_chore)

    # proceed to the results page
    order_list = ['name', 'desc', 'assigned_to', 'points', 'due']
    return render_template('new_chore_results.html', order=order_list, data=res, admin=is_admin)

@app.route('/available_chores', methods=['GET'])
@login_required
def available_chores():
    is_admin = True if session['role'] == 'admin' else False
    chores_list = db.get_available_chores(CHORE_CONN)  # get chores from db (currently a list of json files)
    chores_dict = {}
    for chore in chores_list:  # build a large dict with all of the info in it
        chores_dict[chore.get_attr(attr='name')] = chore.data_dict
    order_list = [k for k in chores_dict]  # get keys(chore names)
    order_list.sort()  # sort the name list, can change sort type
    return render_template('available_chores.html', order=order_list, data=chores_dict, admin=is_admin)


@app.route('/available_rewards', methods=['GET'])
@login_required
def available_rewards():
    is_admin = True if session['role'] == 'admin' else False
    rewards_list = db.get_available_rewards(REWARD_CONN)  # get rewards from db (currently a list of json files)
    rewards_dict = {}
    for reward in rewards_list:  # build a large dict with all of the info in it
        rewards_dict[reward.get_attr(attr='name')] = reward.data_dict
    order_list = [k for k in rewards_dict]  # get keys(reward names)
    order_list.sort()  # sort the name list, can change sort type
    print(rewards_dict)
    return render_template('available_rewards.html', order=order_list, data=rewards_dict, admin=is_admin)



@app.route('/edit_chore')
@app.route('/edit_chore/<chore>', methods=['GET', 'POST'])
@login_required
def edit_chore(chore=None):
    is_admin = True if session['role'] == 'admin' else False
    if chore:
        chore_dict = db.get_chore(CHORE_CONN, chore).data_dict
        return render_template('edit_chore.html', data=chore_dict, admin=is_admin)
    else:
        return redirect(url_for('error'))


@app.route('/edit_reward')
@app.route('/edit_reward/<reward>', methods=['GET', 'POST'])
@login_required
def edit_reward(reward=None):
    is_admin = True if session['role'] == 'admin' else False
    if reward:
        reward_dict = db.get_reward(REWARD_CONN, reward).data_dict
        return render_template('edit_reward.html', data=reward_dict, admin=is_admin)
    else:
        return redirect(url_for('error'))



@app.route('/my_account', methods=['GET'])
@login_required
def my_account():
    is_admin = True if session['role'] == 'admin' else False
    return render_template('my_account.html', admin=is_admin)

@app.route('/new_account', methods=['GET'])
@login_required
@admin_required
def new_account():
    is_admin = True if session['role'] == 'admin' else False
    return render_template('new_account.html', admin=is_admin)


@app.route('/new_account_results', methods=['GET', 'POST'])
@login_required
def new_account_results():
    is_admin = True if session['role'] == 'admin' else False
    res = request.form
    if 'cancel' in res:  # check to see if the cancel button has been pressed
        return redirect(url_for('index'))
    else:
        processed_res, missing = Helpers.process_user_form(res)
        if len(missing) > 0:
            return redirect(url_for('error', data=missing))
        # build a user object, populate it, and stick it in the db
        this_user = User.User(processed_res)
        db.write_user_to_storage(USER_CONN, this_user)
        return render_template('new_account_results.html', data=this_user.data_dict, admin=is_admin)



@app.route('/new_reward', methods=['GET'])
@login_required
def new_reward():
    is_admin = True if session['role'] == 'admin' else False
    return render_template('new_reward.html', admin=is_admin)

@app.route('/new_reward_results', methods=['GET', 'POST'])
@login_required
def new_reward_results():
    is_admin = True if session['role'] == 'admin' else False
    res = request.form
    if 'cancel' in res:  # check to see if the cancel button has been pressed
        return redirect(url_for('index'))
    else:
        processed_res, missing = Helpers.process_reward_form(res)
        if len(missing) > 0:
            return redirect(url_for('error', data=missing))
    # build a reward object, populate it, and stick it in the db
    this_reward = Reward.Reward(processed_res)
    db.write_reward_to_storage(REWARD_CONN, this_reward)
    return render_template('new_reward_results.html', data=this_reward.data_dict, admin=is_admin)




@app.route('/error', methods=['GET'])
def error(missing_list=None):
    return render_template('error.html', data=missing_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


