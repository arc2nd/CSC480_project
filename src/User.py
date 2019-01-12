#!/usr/bin/env python
from datetime import datetime
from app import db
import bcrypt

from Log import _log
VERBOSITY = 1

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # you mean the password hash right?
    email_address = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    date_of_birth = db.Column(db.DateTime)
    points = db.Column(db.Integer)

    def __init__(self):
        self.role_id = 0
        self.points = 0

    def __repr__(self):
        return '<User %r>' % self.username

    def Add(self):
    
        # encrypt the password
        self.password = self.password.encode('utf-8')
        
        self.password = bcrypt.hashpw(self.password, bcrypt.gensalt(12)).decode('utf-8')

        # Default to standard role, start with 0 points
        self.role_id = 1
        self.points = 0

        print(self)

        db.session.add(self)
        db.session.commit()
        
        print(self.username)



    def verify(self, passwd_to_test=None):
        #encrypt password and check against database
        #if so fill up all the possible fields from 
        #stored data
        if bcrypt.checkpw(str(passwd_to_test), self.password):
            return True
        else:
            return False

    def encrypt_passwd(self, plaintext, hashed=None):
        _log(6,VERBOSITY, hashed)
        if not hashed:
            hashed = bcrypt.gensalt(12)
        try:
            ciphertext = bcrypt.hashpw(str(plaintext), str(hashed))
        except:
            ciphertext = 'bad salt: {}'.format(sys.exc_info())

        _log(6, VERBOSITY, ciphertext)
        self.pw_hash=ciphertext
        return ciphertext

    #user ops
    # change me!!
    def get_age(self):
        #calculate age
        return

    # change me!!
    def change_passwd(self, new_pass1=None, new_pass2=None, old_pass=None):
        if new_pass1 == new_pass2:
            if self.verify(old_pass):
                new_hash = self.encrypt_passwd(new_pass)
                self.pw_hash = new_hash
                self.update({'pw_hash': self.pw_hash})


