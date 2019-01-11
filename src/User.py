#!/usr/bin/env python
from datetime import datetime
from app import db

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(255), nullable=False)
	password = db.Column(db.String(255), nullable=False)
	first_name = db.Column(db.String(255), nullable=False)
	email_address = db.Column(db.String(255), nullable=False)
	role_id = db.Column(db.Integer, primary_key=True)
	middle_name = db.Column(db.String(255))
	last_name = db.Column(db.String(255))
	date_of_birth = db.Column(db.DateTime)
	points = db.Column(db.Integer)

	def __init__(self, username, password, first_name, email_address):
		self.username = username
		self.password = password
		self.first_name = first_name
		self.email_address = email_address

	def __repr__(self):
		return '<User %r>' % self.username