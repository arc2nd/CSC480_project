#!/usr/bin/env python

from datetime import datetime
from app import db
from BaseMixin import BaseMixin


class Recurrence(BaseMixin, db.Model):
    __tablename__ = 'recurrences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    frequency_name = db.Column(db.String(255), unique=True, nullable=False)
    frequency_days = db.Column(db.Integer)

    # def __init__(self):

    def __repr__(self):
        return '<Recurrence %r>' % self.frequency_name

    # Create operations

    # Read operations
    @staticmethod
    def GetByFrequencyName(frequency_name):
        """ Return a recurrence by frequency name """
        
        return Recurrence.query.filter_by(frequency_name=frequency_name).first()

    # Update operations

    # Delete operations

    # Utility operations
