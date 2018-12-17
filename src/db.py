#!/usr/bin/env python

# this is probably a good place to put database related functions
# unless we want a database object

#I've temporarly put in some functions to read and write to JSON files
#Could use some more try/except blocks around the file access


import os
import json

from Log import _log

CONN = os.path.join(os.getcwd(), 'chore_storage')

def _validate_storage_location(conn):
    ret_val = True
    if not os.path.exists(conn):
        os.mkdir(conn)
        ret_val = False
    return ret_val


def _write_to_storage(conn, data):
    ret_val = False
    valid = _validate_storage_location(conn)
    with open(os.path.join(conn, "{}.json".format(data['name'].replace(' ', '_'))), 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)
        ret_val = True
    return ret_val


def _read_from_storage(conn, target):
    ret_val = False
    data_dict = {}
    valid = _validate_storage_location(conn)
    with open(os.path.join(conn, '{}'.format(target)), 'r') as fp:
        data_dict = json.load(fp)
        ret_val = True
    return ret_val, data_dict

def get_available_chores(conn):
    all_chores = []
    if os.path.exists(conn):
        all_chores = os.listdir(conn)
    return all_chores

    
