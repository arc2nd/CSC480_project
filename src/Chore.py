#!/usr/bin/env python

from datetime import datetime, timedelta
from app import db
from BaseMixin import BaseMixin
from Recurrence import Recurrence


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

    @staticmethod
    def CreateRecurrence(chore):
        recurrence = Recurrence.GetById(chore.recurrence_id)

        newChore = Chore(chore.name)
        newChore.assigned_to = chore.assigned_to
        newChore.due_date = chore.due_date + timedelta(days=recurrence.frequency_days)
        newChore.description = chore.description
        newChore.points = chore.points
        newChore.complete = False
        newChore.recurrence_id = chore.recurrence_id

        newChore.Add()
        return True

    # Read operations
    @staticmethod
    def GetByUser(user, completed=None):
        """ Return all chores assigned to a single user """
        if(completed == None):
            return Chore.query.filter_by(assigned_to=user.id).all()	

        return Chore.query.filter_by(assigned_to=user.id,complete=completed).all()
    
    @staticmethod
    def GetAll(include_completed=None):
        if(include_completed == None):
            return Chore.query.filter_by(complete=False).all()
        else:
            return Chore.query.filter_by(complete=include_completed).all()


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

        # If the chore repeats
        if chore.recurrence_id != 0:
            Chore.CreateRecurrence(chore)

        chore.complete = True
        
        db.session.commit()

        return True

    # Delete operations

    # Utility operations
    def IsOverdue(self):
        """ Check to see if a chore is overdue"""

        if self.due_date == None:
            return False

        now = datetime.now().date()

        if now >= self.due_date:
            return True

        return False
