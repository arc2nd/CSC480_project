#!/usr/bin/env python

import os
import json
import types
import datetime

import config

class Reward(object):
    """The object to define a Reward"""
    def __init__(self, init_dict=None):
        self.attr_dict = config.REWARD_ATTRS
        self.data_dict = {}
        if isinstance(init_dict, types.DictType):
            self.load_from_dict(init_dict)

    def load_from_db(self, db_conn):
        """load the reward's attributes from a database"""
        if os.path.exists(os.path.join(db_conn, self.data_dict['name'])):
            with open(os.path.join(db_conn, self.data_dict['name']), 'r') as fp: 
                self.data_dict = json.load(fp)
        return

    def update_in_db(self, db_conn):
        """use current reward's attributes to find and update the database entry"""
        return

    def load_from_dict(self, in_dict):
        """load the reward's attributes form a dictionary"""
        for attr in self.attr_dict.keys():
            if attr in in_dict:
                self.data_dict[attr] = in_dict[attr]

    def set_attr(self, attr, value):
        """set a single attribute to a given value"""
        ret_val = False
        if attr in self.attr_dict.keys():
            if isinstance(value, self.attr_dict[attr]):
                    self.data_dict[attr] = value
                    ret_val = True
        return ret_val

    def get_attr(self, attr):
        """get the value of an individual attribute"""
        ret_val = False
        if attr in self.attr_dict.keys() and attr in self.data_dict.keys():
            ret_val = self.data_dict[attr]
        return ret_val

    def attr_exists(self, attr):
        """check if an attribute is in the attr_dict"""
        ret_val = False
        if attr in self.attr_dict.keys():
            ret_val = True
        return ret_val

    def mark_claimed(self):
        """mark this chore as being done on this datetime"""
        now = datetime.datetime.now()
        self.data_dict['claimed'] = now
        return now

    def check_due(self):
        """compare now to the due datetime value"""
        ret_val = False
        now = datetime.datetime.now()
        if 'due' in self.data_dict.keys():
            if now >= self.data_dict['due']:
                self.data_dict['expired'] = True
                self.ret_val = True
        return ret_val

    def assign_to(self, user):
        """assign this chore to a specified user"""
        self.set_attr('assigned_to', user)
        return



