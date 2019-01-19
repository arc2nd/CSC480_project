#!/usr/bin/env python

from datetime import datetime
from app import db


class BaseMixin(object):
    def Add(self):
        """ Add an object """
        db.session.add(self)
        db.session.commit()
        return True

    @classmethod
    def UpdateData(cls):
        """ Update an object """
        db.session.commit()
        return True

    @classmethod
    def GetById(cls, id):
        """ Return a single object by ID """
        return cls.query.filter_by(id=id).first()

    @classmethod
    def GetAll(cls):
        """ Return all instances of an object """
        return cls.query.all()

    @staticmethod
    def Remove(cls):
        """ Remove an object """
        db.session.delete(cls)
        db.session.commit()
        return True
