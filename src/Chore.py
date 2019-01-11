#!/usr/bin/env python
from datetime import datetime
from app import db

class Chore(db.Model):
	__tablename__ = 'chores'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
	due_date = db.Column(db.DateTime)
	name = db.Column(db.String(255), nullable = False)
	description = db.Column(db.String(255))
	points = db.Column(db.Integer)
	complete = db.Column(db.Boolean)
	recurrence = db.Column(db.Enum)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Chore  %r>' % self.name