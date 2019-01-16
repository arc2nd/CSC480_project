#!/usr/bin/env python
from datetime import datetime
from app import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % self.name

    # Create operations
    def Add(role):
        """ Add a role """

        db.session.add(role)
        db.session.commit()

        return True

    # Read operations
    def GetById(role_id):
        """ Return a single role by ID """

        return Role.query.filter_by(id=role_id).first()

    def GetAll():
        """ Return all roles """

        return Role.query.all()

    # Update operations

    # Delete operations
    def Remove(role):
        """ Remove a role """

        db.session.delete(role)
        db.session.commit()

        return True

    # Utility operations