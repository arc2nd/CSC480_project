#!/usr/bin/env python

import os
import unittest
import config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Some repetitive code, is there anyway to import this?
CREDS = config.get_creds('envs.json', crypt=False)

app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = CREDS['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SQLALCHEMY_DATABASE_URI'] = CREDS['SQLALCHEMY_DATABASE_URI']
app.config['ADMIN_ROLE_ID'] = CREDS['ADMIN_ROLE_ID']
app.config['STANDARD_ROLE_ID'] = CREDS['STANDARD_ROLE_ID']

db = SQLAlchemy(app)

import Reward, Role, User, Chore, Recurrence
import ErrorHandler

class Test_UserTestCase(unittest.TestCase):
	def setUp(self):
		user = User.User()
		user.username = 'testing'
		user.password = 'testing'
		user.email_address = 'test@testing.com'
		user.first_name = 'test'
		user.middle_name = 'testy'
		user.last_name = 'testerson'
		user.date_of_birth = '1945-01-01'

		user.Add()

	def tearDown(self):
		user = User.User.GetByUsername('testing')
		User.User.Remove(user)

	def test_create(self):
		exists = False

		user = User.User.GetByUsername('testing')

		if(user):
			exists = True

		assert exists

	def test_delete(self):
		user = User.User()
		user.username = 'testingdelete'
		user.password = 'testingdelete'
		user.email_address = 'testingdelete@testing.com'
		user.first_name = 'test'
		user.middle_name = 'testy'
		user.last_name = 'testerson'
		user.date_of_birth = '1945-01-01'

		user.Add()
		
		exists = True

		user = User.User.GetByUsername('testingdelete')

		User.User.Remove(user)

		if(not user):
			exists = False

		assert exists

	def test_uniqueness(self):
		""" Make sure we can't add users that violate uniqueness rules """
		number_of_users = len(User.User.GetAll())

		user = User.User()
		user.username = 'testing'
		user.password = 'testing'
		user.email_address = 'test@testing.com'
		user.first_name = 'test'
		user.middle_name = 'testy'
		user.last_name = 'testerson'
		user.date_of_birth = '1945-01-01'

		""" Exception expected for non unique username / email address """
		with self.assertRaises(ErrorHandler.ErrorHandler):
			user.Add()

		user.username = 'uniquenow'

		""" Exception expected for non unique email address """
		with self.assertRaises(ErrorHandler.ErrorHandler):
			user.Add()

		user.username = 'testing'
		user.email_address = 'uniquenow@email.com'

		""" Exception expected for non unique username """
		with self.assertRaises(ErrorHandler.ErrorHandler):
			user.Add()

		new_number_of_users = len(User.User.GetAll())

		assert number_of_users == new_number_of_users

	def test_default_role(self):
		user = User.User.GetByUsername('testing')
		assert user.role_id == app.config['STANDARD_ROLE_ID']

if __name__ == '__main__':
	unittest.main()