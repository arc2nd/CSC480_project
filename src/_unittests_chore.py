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

def find_chore(chore_name):
    found_chore = None
    for chore in Chore.Chore.GetAll():
        if chore.name == chore_name:
            found_chore = chore
    return found_chore

class Test_ChoreTestCase(unittest.TestCase):
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

        # build chore to test with
        chore = Chore.Chore('test chore')
        chore.description = 'I am a chore for testing'
        chore.points = 65536
        chore.due_date = '1970-01-01' 
        chore.assigned_to = None
        chore.recurrence_id = 0 #Chore.Recurrence.GetAll()[0]

        chore.Add()
 

    def tearDown(self):
        Chore.Chore.Remove(find_chore('test chore'))

        user = User.User.GetByUsername('testing')
        User.User.Remove(user)


    def test_create(self):
        exists = False

        if find_chore('test chore'):
            exists = True

        assert exists


    def test_assign(self):
        assigned = False
        assigned = find_chore('test chore').AssignTo(User.User().GetByUsername('testing'))

        assert assigned

    def test_unassign(self):
        unassigned = False
        unassigned = find_chore('test chore').Unassign()
        assert unassigned

   
    """ 
    def test_complete(self):
        complete = False
        print(find_chore('test chore'))
        print(find_chore('test chore').recurrence_id)
        complete = find_chore('test chore').MarkCompleted()
        assert complete
    """
    
    def test_overdue(self):
        overdue = False
        overdue = find_chore('test chore').IsOverdue()
        assert overdue


    def test_delete(self):
        # built chore to test with
        chore = Chore.Chore('test chore to delete')
        chore.description = 'I am a chore for deleting'
        chore.points = 65536
        chore.due_date = None
        chore.assign_to = None

        chore.Add()
        
        exists = True

        found_chore = None
        for chore in Chore.Chore.GetAll():
            if chore.name == 'test chore to delete':
                found_chore = chore
        if found_chore:
            Chore.Chore.Remove(found_chore)

        if(not found_chore):
            exists = False

        assert exists
 

if __name__ == '__main__':
    unittest.main()


