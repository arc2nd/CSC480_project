#!/usr/bin/env python

import datetime

class Reward(object):
    def __init__(self):
        self.name = None
        self.desc = None
        self.due = None
        self.expired = False
        self.points = 0
        self.creator = None
        self.assigned_to = None
        self.claimed = False
        self.recurring = None
        self.id = 0

    def load_from_db(self, db_conn):
        return

    def update_in_db(self, db_conn):
        return

    def mark_claimed(self):
        self.claimed = True
        return

    def check_due(self):
        now = datetime.datetime.now()
        if now >= due:
            self.expired = True
        return

    def claim(self, user):
        self.assigned_to = user
        self.claimed = True
        return
