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
    password = db.Column(db.String(60), nullable=False)
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

    # Create operations
    @staticmethod
    def Add(user):
        """ Add a user """

        # encrypt the password
        user.password = User.EncryptPassword(user.password)

        # Default to standard role, start with 0 points
        user.role_id = 1
        user.points = 0

        db.session.add(user)
        db.session.commit()

        return True

    # Read operations
    @staticmethod
    def GetById(user_id):
        """ Return a single user by ID """

        return User.query.filter_by(id=user_id).first()
    
    @staticmethod
    def GetByUsername(username):
        """ Return a user by username """
        
        return User.query.filter_by(username=username).first()

    @staticmethod
    def GetAll():
        """ Return all users """

        return User.query.all()

    # Update operations
    def UpdatePassword(self, new_password=None, new_password_verify=None, old_password=None):
        """ Updates a user's password """
        if new_password == new_password_verify:
            if self.VerifyPassword(old_password):
                new_password = User.EncryptPassword(new_password)
                self.password = new_password
                db.session.commit()
                return True
        return False

    # Delete operations
    @staticmethod
    def Remove(user):
        """ Remove a user """

        db.session.delete(user)
        db.session.commit()

        return True

    # Utility operations
    @staticmethod
    def EncryptPassword(password_to_encrypt):
        """ Encode, encrypt, and return the hashed password"""
        password_to_encrypt = password_to_encrypt.encode('utf-8')
        password_to_encrypt = bcrypt.hashpw(password_to_encrypt, bcrypt.gensalt(12)).decode('utf-8')
        
        return password_to_encrypt

    def VerifyPassword(self, password_to_test=None):
        """ Verifies that an entered password is correct """
        #encrypt password and check against database
        if(bcrypt.checkpw(password_to_test.encode('utf-8'), self.password.encode('utf-8'))):
            return True
        else:
            return False


