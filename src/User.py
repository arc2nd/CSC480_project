#!/usr/bin/env python

import os
import json
import types
import datetime

import config

class User(object):
    """The object to define a Chore"""
    def __init__(self, init_dict=None):
        self.attr_dict = config.USER_ATTRS
        self.data_dict = {}
        if isinstance(init_dict, types.DictType):
            self.load_from_dict(init_dict)

    def load_from_db(self, db_conn):
        """load the user's attributes from a database"""
        if os.path.exists(os.path.join(db_conn, self.data_dict['name'])):
            with open(os.path.join(db_conn, self.data_dict['name']), 'r') as fp:
                self.data_dict = json.load(fp)
        return

    def update_in_db(self, db_conn):
        """use current user's attributes to find and update the database entry"""
        with open(os.path.join(db_conn, self.data_dict['name'], 'w')) as fp:
            json.dump(self.data_dict, fp, indent=4, sort_keys=True)
        return

    def load_from_dict(self, in_dict):
        """load the user's attributes from a dictionary"""
        for attr in self.attr_dict.keys():
            if attr in in_dict:
                self.data_dict[attr] = in_dict[attr]

    def set_attr(self, attr, value):
        """set a single attribute to a given value"""
        ret_val = False
        if attr in self.attr_dict.keys():
            if isinstance(value, self.attr_dict[attr]):
                    self.data_dict[attr] = value
                    ret_val = True
        return ret_val

    def get_attr(self, attr):
        """get the value of an individual attribute"""
        ret_val = False
        if attr in self.attr_dict.keys() and attr in self.data_dict.keys():
            ret_val = self.data_dict[attr]
        return ret_val

    #CRUD ops
    def verify(self, passwd=None):
        #encrypt password and check against database
        #if so fill up all the possible fields from 
        #stored data
        if passwd == self.get_attr(attr='pw_hash'):
            return True
        else:
            return False

        """
        expected_hashed = self.get_pw_from_db() #who you say you are
        hashed_passwd = self.encrypt_passwd(passwd, expected_hashed) #replace this with whatever hashing is being used
        print(hashed_passwd)
        if hashed_passwd != 'error' and hashed_passwd == expected_hashed:
            self.load_from_db(self.name)
            return True
        else:
            return False
"""
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


