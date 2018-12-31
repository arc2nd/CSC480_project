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
#app.secret_key = 'i am a secret'
app.secret_key = Helpers.get_creds('envs.crypt')['SECRET_KEY']


# set some globals
VERBOSITY = 1
CHORE_CONN = db.CHORE_CONN
USER_CONN = db.USER_CONN
REWARD_CONN = db.REWARD_CONN

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        for i in session:
            _log(1, VERBOSITY, '{} :: {}'.format(i, session[i]))
        if 'logged_in' not in session:
            return redirect(url_for('login')) #, next=request.url))
        return f(*args, **kwargs)
    return decorated_function




# The actual website endpoints

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
def index():
    user_list = db.get_all_users(conn=USER_CONN)
    user_dict = {}
    for user in user_list:
        u_dict = db.get_user(conn=USER_CONN, name=user)
        user_dict[user] = u_dict.data_dict
    return render_template('index.html', data={'users': user_dict})

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        res = request.form
        if Helpers.verify_user(res['username']):
            u = db.get_user(conn=USER_CONN, name=res['username'])
            if u.verify(passwd=res['password']):
                ts = calendar.timegm(datetime.datetime.now().timetuple())
                session['user'] = u.get_attr(attr='name')
                session['logged_in'] = ts
                for i in session:
                    print('{} :: {}'.format(i, session[i]))
                return redirect(url_for('index'))
    except:
        print(sys.exc_info())
        traceback.print_tb(sys.exc_info()[-1])
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_name = session['user']
    session.pop('user')
    session.pop('logged_in')
    for i in session:
        print('{} :: {}'.format(i, session[i]))
    return render_template('logout.html', user=user_name)
    return render_template('logout.html')


@app.route('/chores', methods=['GET', 'POST'])
@app.route('/chores/<user>', methods=['GET', 'POST'])
@login_required
def chores(user=None):
    if user:
        user_chores = db.get_user_chores(CHORE_CONN, user)
        chores_dict = {}
        for c in user_chores:
            chores_dict[c] = db.get_chore(CHORE_CONN, c).data_dict
    return render_template('chores.html', data=chores_dict)

@app.route('/new_chore', methods=['GET'])
@login_required
def new_chore():
    return render_template('new_chore.html')


@app.route('/new_chore_results', methods=['GET', 'POST'])
@login_required
def new_chore_results():
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
    return render_template('new_chore_results.html', order=order_list, data=res)

@app.route('/available_chores', methods=['GET'])
@login_required
def available_chores():
    chores_list = db.get_available_chores(CHORE_CONN)  # get chores from db (currently a list of json files)
    chores_dict = {}
    for chore in chores_list:  # build a large dict with all of the info in it
        status, this_chore = db._read_from_storage(CHORE_CONN, chore)
        chores_dict[chore] = this_chore
    order_list = [k for k in chores_dict]  # get keys(chore names)
    order_list.sort()  # sort the name list, can change sort type
    return render_template('available_chores.html', order=order_list, data=chores_dict)


@app.route('/available_rewards', methods=['GET'])
@login_required
def available_rewards():
    rewards_list = db.get_available_rewards(REWARD_CONN)  # get rewards from db (currently a list of json files)
    rewards_dict = {}
    for reward in rewards_list:  # build a large dict with all of the info in it
        rewards_dict[reward.get_attr(attr='name')] = reward.data_dict
    order_list = [k for k in rewards_dict]  # get keys(reward names)
    order_list.sort()  # sort the name list, can change sort type
    print(rewards_dict)
    return render_template('available_rewards.html', order=order_list, data=rewards_dict)



@app.route('/edit_chore')
@app.route('/edit_chore/<chore>', methods=['GET', 'POST'])
@login_required
def edit_chore(chore=None):
    if chore:
        chore_dict = db.get_chore(CHORE_CONN, chore).data_dict
        return render_template('edit_chore.html', data=chore_dict)
    else:
        return redirect(url_for('error'))


@app.route('/edit_reward')
@app.route('/edit_reward/<reward>', methods=['GET', 'POST'])
@login_required
def edit_reward(reward=None):
    if reward:
        reward_dict = db.get_reward(REWARD_CONN, reward).data_dict
        return render_template('edit_reward.html', data=reward_dict)
    else:
        return redirect(url_for('error'))



@app.route('/my_account', methods=['GET'])
@login_required
def my_account():
    return render_template('my_account.html')

@app.route('/new_account', methods=['GET'])
@login_required
def new_account():
    return render_template('new_account.html')


@app.route('/new_account_results', methods=['GET', 'POST'])
@login_required
def new_account_results():
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
        return render_template('new_account_results.html', data=this_user.data_dict)





@app.route('/new_reward', methods=['GET'])
@login_required
def new_reward():
    return render_template('new_reward.html')

@app.route('/new_reward_results', methods=['GET', 'POST'])
@login_required
def new_reward_results():
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
    return render_template('new_reward_results.html', data=this_reward.data_dict)




@app.route('/error', methods=['GET'])
def error(missing_list=None):
    return render_template('error.html', data=missing_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


