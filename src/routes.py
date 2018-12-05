#!/usr/bin/env python


from flask import Flask, render_template, Response, redirect, url_for, request, session, flash

app = Flask(__name__)

VERBOSITY = 1

def _log(priority, msg):
    if VERBOSITY >= priority:
        print(msg)


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

