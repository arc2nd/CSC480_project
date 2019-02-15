#!/usr/bin/env python

from datetime import datetime
from app import db
from BaseMixin import BaseMixin
from Log import Log, LogType

_log = Log()

class Reward(BaseMixin, db.Model):
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

    # Read operations

    # Update operations

    # Delete operations

    # Utility operations
    @staticmethod
    def Claim(reward, user):
        """ Claim a reward """
        if user.points >= reward.points:
            user.points -= reward.points

            db.session.commit()

            return True
        
        return False

    @staticmethod
    def Notify(reward, user):
        import notifications
        try:
            notifications.send_reward_claim_notice(reward=reward, user=user)
        except:
            _log.log("An error has occurred in sending a notification about reward {} for user {}".format(reward.name, user.username), LogType.ERROR)
        return
