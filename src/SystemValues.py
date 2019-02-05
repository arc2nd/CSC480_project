#!/usr/bin/env python

from app import db
from BaseMixin import BaseMixin


class SystemValues(BaseMixin, db.Model):
    __tablename__ = 'systemvalues'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    value_bool = db.Column(db.Boolean)
    value_date = db.Column(db.DateTime)
    value_int = db.Column(db.Integer)
    value_string = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<SystemValue  %r>' % self.name

    # Create operations
    
    # Read operations

    # Update operations

    # Delete operations

    # Utility operations
