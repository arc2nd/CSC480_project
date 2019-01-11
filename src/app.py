from flask import Flask, render_template, Response, redirect, url_for, request, session, abort, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from Log import _log

import traceback
import sys
from functools import wraps

import User
import Helpers
import os

# Static files path
app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)

# set some globals
VERBOSITY = 1


# Route decorators
def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		print("login check")
		if 'logged_in' not in session:
			print("user not logged in")
			return redirect(url_for('login_form'))
		else:
			print("user logged in")
		return f(*args, **kwargs)
	return decorated_function

def admin_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		print("admin check")
		if session['role'] == 0:
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

	result = User.User.query.filter_by(username=POST_USERNAME, password=POST_PASSWORD).first()

	if(result):
		session['logged_in'] = True
		session['role'] = result.role_id
		print('logged in')
	else:
		print('bad credentials')

	return index()

@app.route('/login', methods=['GET'])
def login_form():
	return render_template('login.html')

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
@app.route('/', methods=['GET', 'POST'])
def index():
	if not session.get('logged_in'):
		return login_form()
	else:
		return render_template('index.html')

# User routes
@app.route('/users', methods=['GET', 'POST'])
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

if __name__ == '__main__':
	app.secret_key = os.urandom(12)
	app.run()