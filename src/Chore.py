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

    # Create operations
    def Add(chore):
        """ Add a chore """

        db.session.add(chore)
        db.session.commit()

        return

    # Read operations
    def GetById(chore_id):
        """ Return a single chore by ID """

        return Chore.query.filter_by(id=chore_id).first()

    def GetAll():
        """ Return all chores """

        return Chore.query.all()

    # Update operations
    def AssignTo(self, user):
        """ Assign a chore to a user """
        chore = Chore.GetById(self.id)
        chore.assigned_to = user.id
        db.session.commit()

        return True

    def MarkCompleted(self):
        """ Mark a chore as completed """
        
        chore = Chore.GetById(self.id)
        chore.complete = True
        db.session.commit()

        return

    # Delete operations
    def Remove(chore):
        """ Remove a chore """

        db.session.delete(chore)
        db.session.commit()

        return

    # Utility operations
    def IsOverdue(self):
        """ Check to see if a chore is overdue"""

        if self.due_date == None:
            return False

        now = datetime.now()

        if now >= self.due_date:
            return True

        return False
