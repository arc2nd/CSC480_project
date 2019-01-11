#!/usr/bin/env python
from datetime import datetime
from app import db
import bcrypt

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
	username = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
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