#!/usr/bin/env python

from datetime import datetime
from app import db
from BaseMixin import BaseMixin


class Chore(BaseMixin, db.Model):
    pass
    __tablename__ = 'chores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    due_date = db.Column(db.DateTime)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    points = db.Column(db.Integer)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    recurrence_id = db.Column(db.Integer, db.ForeignKey("recurrences.id"), nullable=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Chore  %r>' % self.name

    # Create operations
    def Add(self):
        """ Add a chore """

        """ Default to incomplete """
        self.complete = False

        db.session.add(self)
        db.session.commit()
        return True

    # Read operations
    @staticmethod
    def GetByUser(user, completed):
        """ Return all chores assigned to a single user """

        return Chore.query.filter_by(assigned_to=user.id,complete=completed).all()

    # Update operations
    def AssignTo(self, user):
        """ Assign a chore to a user """
        chore = Chore.GetById(self.id)
        chore.assigned_to = user.id
        db.session.commit()

        return True

    def Unassign(self):
        """ Unassign this chore so that it is claimable """
        chore = Chore.GetById(self.id)
        chore.assigned_to = None
        db.session.commit()

        return True

    def MarkCompleted(self):
        """ Mark a chore as completed """
        
        chore = Chore.GetById(self.id)
        chore.complete = True
        db.session.commit()

        return True

    # Delete operations

    # Utility operations
    def IsOverdue(self):
        """ Check to see if a chore is overdue"""

        if self.due_date == None:
            return False

        now = datetime.now()

        if now >= self.due_date:
            return True

        return False
