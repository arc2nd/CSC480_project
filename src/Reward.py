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

    def Add(self):
        print(self)
        db.session.add(self)
        db.session.commit()