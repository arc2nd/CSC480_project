#!/usr/bin/env python
#db.py

# this is probably a good place to put database related functions
# unless we want a database object

#I've temporarly put in some functions to read and write to JSON files
#Could use some more try/except blocks around the file access


import os
import json

import User
import Chore
from Log import _log

CHORE_CONN = os.path.join(os.getcwd(), 'chore_storage')
USER_CONN = os.path.join(os.getcwd(), 'user_storage')

def _validate_storage_location(conn):
    """make sure the storage location actually exists
       if not,  make it
    """
    ret_val = True
    if not os.path.exists(conn):
        os.mkdir(conn)
        ret_val = False
    return ret_val


def _write_to_storage(conn, data):
    """write a data dict to a location/connection"""
    ret_val = False
    valid = _validate_storage_location(conn)
    with open(os.path.join(conn, "{}.json".format(data['name'].replace(' ', '_'))), 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)
        ret_val = True
    return ret_val


def _read_from_storage(conn, target):
    """read a record from the location/connection"""
    ret_val = False
    data_dict = {}
    valid = _validate_storage_location(conn)
    with open(os.path.join(conn, '{}'.format(target)), 'r') as fp:
        data_dict = json.load(fp)
        ret_val = True
    return ret_val, data_dict

def write_chore_to_storage(conn, chore):
    """write a chore object to a location/connection"""
    _write_to_storage(conn, chore.data_dict)

def write_reward_to_storage(conn, reward):
    """write a reward object to a location/connection"""
    _write_to_storage(conn, reward.data_dict)

def get_all_chores(conn):
    """get all chores, will later filter by user"""
    all_chores = []
    if os.path.exists(conn):
        all_chores = os.listdir(conn)
    return all_chores

def get_all_users(conn):
    all_users = []
    if os.path.exists(conn):
        all_users = os.listdir(conn)
    return all_users

def get_user(conn=None, name=None):
    all_users = get_all_users(conn)
    for u in all_users:
        if name in u:
            m = User.User()
            m.set_attr(attr='name', value=name)
            m.load_from_db('user_storage')
            return m

def get_available_chores(conn):
    return get_user_chores(conn=conn, user='')

def get_chore(conn=None, name=None):
    all_chores = get_all_chores(conn)
    for c in all_chores:
        if name in c:
            c = Chore.Chore()
            c.set_attr(attr='name', value=name)
            c.load_from_db('chore_storage')
            return c

def get_user_chores(conn=None, user=None):
    all_chores = get_all_chores(conn)
    user_chores = []
    for c in all_chores:
        c_dict = get_chore(conn, c).data_dict
        if user == c_dict['assigned_to']:
            user_chores.append(c)
    return user_chores
