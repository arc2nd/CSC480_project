#!/usr/bin/env python

import os
import json

from flask import Flask, render_template, Response, redirect, url_for, request, session, flash

import db
import Helpers


app = Flask(__name__)

# set some globals
VERBOSITY = 1
DB_CONN = db.CONN


# it'd probably be a good idea to put this into a log.py file
# or, you know, use a real logging scheme
def _log(priority, msg):
    if VERBOSITY >= priority:
        print(msg)


# The actual website endpoints

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')


@app.route('/chores', methods=['GET', 'POST'])
def chores():
    chores_dict = {'Take out trash': 1,  # build a fake chore dict
                   'Take out recycling': 1, 
                   'Clean kitty litter': 2, 
                   'Clean chicken coop': 3, 
                   'Clean playroom': 1, 
                   'Wash dishes': 2, 
                   'Clean your room': 1, 
                   'Clean bathroom': 3, 
                   'Vacuum': 1}
    return render_template('chores.html', data=chores_dict)


@app.route('/new_chore_results', methods=['GET', 'POST'])
def new_chore_results():
    res = request.form
    if 'cancel' in res:  # check to see if the cancel button has been pressed
        return redirect(url_for('index'))
    _log(6, res)
    processed_res, missing = Helpers._process_chore_form(res)  # process the form results and validate
    _log(6, missing)
    if len(missing) > 0:
        return render_template('error.html', data=missing)
    db._write_to_storage(DB_CONN, processed_res)  # write chore to db (currently json storage)
    res_str = json.dumps(processed_res, sort_keys=True, indent=4)
    _log(6, res_str)
    order_list = ['name', 'desc', 'assigned_to', 'points', 'due']
    return render_template('new_chore_results.html', order=order_list, data=res)


@app.route('/available', methods=['GET'])
def available():
    chores_list = db.get_available_chores(DB_CONN)  # get chores from db (currently a list of json files)
    chores_dict = {}
    for chore in chores_list:  # build a large dict with all of the info in it
        with open(os.path.join(DB_CONN, chore), 'r') as fp:
            this_chore = json.load(fp)
        chores_dict[chore] = this_chore
    order_list = [k for k in chores_dict]  # get keys(chore names)
    order_list.sort()  # sort the name list, can change sort type
    return render_template('available.html', order=order_list, data=chores_dict)


@app.route('/new_chore', methods=['GET'])
def new_chore():
    return render_template('new_chore.html')


@app.route('/my_account', methods=['GET'])
def my_account():
    return render_template('my_account.html')


@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


