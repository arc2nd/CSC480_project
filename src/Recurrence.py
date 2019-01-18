#!/usr/bin/env python
from datetime import datetime
from app import db
import bcrypt

from Log import _log
VERBOSITY = 1

class Recurrence(db.Model):
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
    def GetById(recurrence_id):
        """ Return a single recurrence by ID """

        return Recurrence.query.filter_by(id=recurrence_id).first()
    
    @staticmethod
    def GetByFrequencyName(frequency_name):
        """ Return a recurrence by frequency name """
        
        return Recurrence.query.filter_by(frequency_name=frequency_name).first()

    @staticmethod
    def GetAll():
        """ Return all recurrences """

        return Recurrence.query.all()

    # Update operations

    # Delete operations

    # Utility operations
