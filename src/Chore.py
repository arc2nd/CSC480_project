#!/usr/bin/env python

import datetime

class Chore(object):
    def __init__(self):
        self.name = None
        self.desc = None
        self.due = None
        self.expired = False
        self.points = 0
        self.creator = None
        self.assigned_to = None
        self.done = False
        self.recurring = None
        self.id = 0

    def load_from_db(self, db_conn):
        return

    def update_in_db(self, db_conn):
        return

    def mark_done(self):
        self.done = True
        return

    def check_due(self):
        now = datetime.datetime.now()
        if now >= self.due:
            self.expired = True
        return

    def assign_to(self, user):
        self.assigned_to = user
        return
