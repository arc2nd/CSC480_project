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

def find_reward(reward_name):
    found_reward = None
    for reward in Reward.Reward.GetAll():
        if reward.name == reward_name:
            found_reward = reward
    return found_reward

class Test_RewardTestCase(unittest.TestCase):
    def setUp(self):
        # build user to test with
        user = User.User()
        user.username = 'testing'
        user.password = 'testing'
        user.email_address = 'test@testing.com'
        user.first_name = 'test'
        user.middle_name = 'testy'
        user.last_name = 'testerson'
        user.date_of_birth = '1945-01-01'

        user.Add()

        # build reward to test with
        reward = Reward.Reward('test reward')
        reward.description = 'I am a reward for testing'
        reward.points = 5 

        reward.Add()

    def tearDown(self):
        Reward.Reward.Remove(find_reward('test reward'))
        user = User.User.GetByUsername('testing')
        User.User.Remove(user)

    def test_create(self):
        exists = False

        reward = find_reward('test reward')

        if(reward):
            exists = True

        assert exists

    
    def test_delete(self):
        reward = Reward.Reward('test reward to delete')
        reward.description = 'I am a reward for deleting'
        reward.points = 65536

        reward.Add()
        
        exists = True

        reward = find_reward('test reward to delete')

        Reward.Reward.Remove(reward)

        if(not reward):
            exists = False

        assert exists
    
    
    def test_claim(self):
        user = User.User.GetByUsername('testing')
        user.AddPoints(100)
        reward = find_reward('test reward')
        claimed = Reward.Reward.Claim(reward, user)
        assert claimed 

if __name__ == '__main__':
    unittest.main()
