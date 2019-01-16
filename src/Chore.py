#!/usr/bin/env python

from datetime import datetime
from app import db


class Chore(db.Model):
    __tablename__ = 'chores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    due_date = db.Column(db.DateTime)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    points = db.Column(db.Integer)
    complete = db.Column(db.Boolean)
    #recurrence = db.Column(db.Enum)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Chore  %r>' % self.name

    def Add(self):
        print(self)
        db.session.add(self)
        db.session.commit()
        print(self.name)

    def mark_done(self):
        """mark this chore as being done on this datetime"""
        now = datetime.datetime.now()
        self.complete = now
        return now

    def check_due(self):
        """compare now to the due datetime value"""
        ret_val = False
        now = datetime.now()
        if now >= self.data_dict['due']:
            # set an expired flag
            # we can also set a threshold and use this function to spawn an reminder later
            #self.expired = True
            ret_val = True
        return ret_val

    def assign_to(self, user):
        """assign this chore to a specified user"""
        self.assigned_to = user
        
        chore = db.session.query(Chore).get(self.id)

        chore.assigned_to = user.id

        db.session.commit()

        return True
