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

class Test_RecurrenceTestCase(unittest.TestCase):
    def setUp(self):
        return

    def tearDown(self):
        return

    def test_daily(self):
        assert Recurrence.Recurrence.GetByFrequencyName('daily') 

    def test_weekly(self):
        assert Recurrence.Recurrence.GetByFrequencyName('weekly')

    def test_does_not_repeat(self):
        assert Recurrence.Recurrence.GetByFrequencyName('does not repeat')

    def test_negative(self):
        assert not Recurrence.Recurrence.GetByFrequencyName('fake')

if __name__ == '__main__':
    unittest.main()
