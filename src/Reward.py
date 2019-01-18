#!/usr/bin/env python
from datetime import datetime
from app import db


class Reward(db.Model):
    __tablename__ = 'rewards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))
    points = db.Column(db.Integer, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Reward  %r>' % self.name

    # Create operations
    def Add(reward):
        """ Add a reward """

        db.session.add(reward)
        db.session.commit()

        return True

    # Read operations
    @staticmethod
    def GetById(reward_id):
        """ Return a single reward by ID """

        return Reward.query.filter_by(id=reward_id).first()

    @staticmethod
    def GetAll():
        """ Return all rewards """

        return Reward.query.all()

    # Update operations

    # Delete operations
    @staticmethod
    def Remove(reward):
        """ Remove a reward """

        db.session.delete(reward)
        db.session.commit()

        return True

    # Utility operations
    @staticmethod
    def Claim(reward, user):
        """ Claim a reward """
        if user.points >= reward.points:
            user.points -= reward.points

            db.session.commit()

            return True
        
        return False