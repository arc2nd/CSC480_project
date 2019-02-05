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

def find_role(role_name):
    found_role = None
    for role in Role.Role.GetAll():
        if role.name == role_name:
            found_role = role
    return found_role


class Test_RoleTestCase(unittest.TestCase):
    def setUp(self):
        return  

    def tearDown(self):
        return

    def test_admin(self):
        assert find_role('Administrator')

    def test_standard(self):
        assert find_role('Standard')

if __name__ == '__main__':
    unittest.main()
