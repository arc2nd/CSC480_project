#!/usr/bin/env python
from datetime import datetime
from app import db

class Reward(db.Model):
    __tablename__ = 'rewards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable = False)
    description = db.Column(db.String(255))
    points = db.Column(db.Integer, nullable = False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Reward  %r>' % self.name

    def mark_claimed(self):
        """mark this chore as being done on this datetime"""
        now = datetime.datetime.now()
        self.data_dict['claimed'] = now
        return now

    def check_due(self):
        """compare now to the due datetime value"""
        ret_val = False
        now = datetime.now()
        if now >= self.data_dict['due']:
            # set an expired flag
            #self.expired = True
            self.ret_val = True
        return ret_val

    def assign_to(self, user):
        """assign this chore to a specified user"""
        self.assigned_to = user
        return

