#!/usr/bin/env python
from datetime import datetime
from app import db

class Role(db.Model):
	__tablename__ = 'roles'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(255), unique=True, nullable=False)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Role %r>' % self.name