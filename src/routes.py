#!/usr/bin/env python

import json

from flask import Flask, render_template, Response, redirect, url_for, request, session, flash

import Helpers


app = Flask(__name__)

VERBOSITY = 1

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
    chores_dict = {'Take out trash': 1, 
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
    order_list = ['name', 'desc', 'assigned_to', 'points', 'due']
    res = request.form
    processed_res, missing = Helpers._process_chore_form(res)
    _log(1, missing)
    if len(missing) > 0:
        return render_template('error.html', data=missing)
    res_str = json.dumps(processed_res, sort_keys=True, indent=4)
    _log(1, res_str)
    return render_template('new_chore_results.html', order=order_list, data=res)

@app.route('/available', methods=['GET'])
def available():
    return render_template('available.html')


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

