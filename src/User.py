#!/usr/bin/env python

import os
import sys
import bcrypt
import datetime

class User(object):
    def __init__(self, name=None):
        self.name = name
        self.email = None
        self.first_name = None
        self.last_name = None
        self.middle_name = None
        self.dob = None
        self.points = 0
        self.style = None
        self.timeout = 20
        self.pw_hash = None
        self.id = 0

        self.verbosity = 1

    def _log(self, priority, msg, logfile=None):
        if self.verbosity >= priority:
            print(msg)
            if os.path.exists(logfile):
                with open(logfile, 'a') as fp:
                    fp.write(msg)

    #CRUD ops
    def verify(self, passwd=None):
        #encrypt password and check against database
        #if so fill up all the possible fields from 
        #stored data
        expected_hashed = self.get_pw_from_db() #who you say you are
        hashed_passwd = self.encrypt_passwd(passwd, expected_hashed) #replace this with whatever hashing is being used
        if hashed_passwd != 'error' and hashed_passwd == expected_hashed:
            self.load_from_db(self.name)
            return True
        else:
            return False

    def enroll(self):
        #add user to user database
        return

    def update(self):
        #update user info to database
        return

    def delete(self):
        #delete user from database
        return

    def get_pw_from_db(self):
        #talk to the db, and get the stored encrypted password for this user
        return

    def load_from_db(self):
        #talk to the db, load all the attrs for this username into the current object
        return

    #rest ops
    def encrypt_passwd(self, plaintext, hashed=None):
        self._log(6, hashed)
        if not hashed:
            hashed = bcrypt.gensalt(8)
        try:
            ciphertext = bcrypt.hashpw(str(plaintext), str(hashed))
        except:
            ciphertext = 'bad salt: {}'.format(sys.exc_info())

        #how are you hashing passwords? I'm using a REST service
        #resp = requests.post('http://localhost:5002/crypt', data={'plaintext': plaintext, 'hash':hashed})
        ##process response for extraneous characters
        #if resp.ok:
        #    ciphertext = resp.text[1:-2]
        #else:
        #    ciphertext = 'error'
        self._log(6, ciphertext)
        self.pw_hash=ciphertext
        return ciphertext

    #user ops
    def get_age(self):
        #calculate age
        return

    def change_passwd(self, new_pass1=None, new_pass2=None, old_pass=None):
        if new_pass1 == new_pass2:
            if self.verify(old_pass):
                new_hash = self.encrypt_passwd(new_pass)
                self.pw_hash = new_hash
                self.update({'pw_hash': self.pw_hash})

    def to_dict(self):
        u_dict = {}
        u_dict['name'] = self.name
        u_dict['email'] = self.email
        u_dict['first_name'] = self.first_name
        u_dict['middle_name'] = self.middle_name
        u_dict['last_name'] = self.last_name
        u_dict['dob'] = self.dob
        u_dict['points'] = self.points
        u_dict['style'] = self.style
        u_dict['timeout'] = self.timeout
        u_dict['pw_hash'] = self.pw_hash
        u_dict['id'] = self.id
        return u_dict

    def from_dict(self, u_dict):
        self.name = u_dict['name']
        self.email = u_dict['email']
        self.first_name = u_dict['first_name']
        self.middle_name = u_dict['middle_name']
        self.last_name = u_dict['last_name']
        self.dob = u_dict['dob']
        self.points = u_dict['points']
        self.style = u_dict['style']
        self.timeout = u_dict['timeout']
        self.pw_hash = u_dict['pw_hash']
        self.id = u_dict['id']


