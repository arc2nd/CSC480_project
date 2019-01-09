#!/usr/bin/env python
#Helpers.py
#this is a good spot to put functions that don't really fit other descriptions

import os
import json
import datetime
import subprocess

import bcrypt

import config
from Log import _log

MANDATORY_CHORE_KEYS = ['name']
OPTIONAL_CHORE_KEYS= ['points', 'desc', 'due']
POSSIBLE_CHORE_KEYS = MANDATORY_CHORE_KEYS + OPTIONAL_CHORE_KEYS

MANDATORY_REWARD_KEYS = ['name', 'points']
OPTIONAL_REWARD_KEYS = ['desc', 'expires']
POSSIBLE_REWARD_KEYS = MANDATORY_REWARD_KEYS + OPTIONAL_REWARD_KEYS

MANDATORY_USER_KEYS = ['name', 'email', 'type', 'pw_hash']
OPTIONAL_USER_KEYS = ['first', 'middle', 'last', 'dob', 'style']
POSSIBLE_USER_KEYS = MANDATORY_USER_KEYS + OPTIONAL_USER_KEYS

VERBOSITY = 1

CHORE_ATTRS = config.CHORE_ATTRS
REWARD_ATTRS = config.REWARD_ATTRS
USER_ATTRS = config.USER_ATTRS

def get_creds(path, crypt=False):
    if crypt:
        cmd = "openssl des3 -salt -d -in %s -pass pass:%s" % (path, os.path.basename(path))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        if (output):
            try:
                j = json.loads(output)
                return j
            except:
                return output
    else:
        if os.path.exists(path):
            with open(path, 'r') as fp:
                j = json.load(fp)
            return j


def _convert_form_keys(in_dict, attr_dict):
    """Converts an ImmutableDict to a regular Dict
       and converts type if necessary
    """
    ret_dict = {}
    pass_1 = pass_2 = None
    for key in in_dict:
        _log(6, VERBOSITY, key)
        if 'submit' not in key.lower():
            val = in_dict[key]
            try:
                _log(6, VERBOSITY, '{} :: {}'.format(val, type(val)))
                _log(6, VERBOSITY, '{} :: {}'.format(key, attr_dict[key]))
            except:
                print('')
            if key == 'pass_1':
                pass_1 = in_dict[key]
                print('pass_1: {}'.format(in_dict[key]))
            elif key == 'pass_2':
                pass_2 = in_dict[key]
                print('pass_2: {}'.format(in_dict[key]))
            elif not isinstance(val, attr_dict[key]):
                if isinstance('string', attr_dict[key]):
                    _log(6, VERBOSITY, 'coercing to string: {}'.format(val))
                    val = '{}'.format(val)
                if isinstance(0.0, attr_dict[key]):
                    _log(6, VERBOSITY, 'coercing to float: {}'.format(val))
                    val = float(val)
                if isinstance(1, attr_dict[key]):
                    _log(6, VERBOSITY, 'coercing to int: {}'.format(val))
                    val = int(val)
                if isinstance(datetime.datetime.now(), attr_dict[key]):
                    _log(6, VERBOSITY, 'coercing to datetime: {}'.format(val))
                    val = _convert_str_to_dt(val)
            ret_dict[key] = val
        else:
            _log(6, VERBOSITY, 'submit', 'chore.log')
    if pass_1 and pass_2:
        ret_dict.pop('pass_1')
        ret_dict.pop('pass_2')
        _log(1, VERBOSITY, 'have pass_1 and _2')
        if pass_1 == pass_2:
            _log(1, VERBOSITY, 'pass_1 and _2 match')
            ret_dict['pw_hash'] = bcrypt.hashpw(str(pass_1), bcrypt.gensalt(8))
    return ret_dict

def _convert_str_to_dt(val):
    """Convert a string (mm/dd/yy) to a datetime object"""
    return val

def _validate_form_keys(in_dict, mandatory_list):
    """Make sure that the mandatory keys have values"""
    missing = []
    for key in in_dict:
        if key in mandatory_list:
            _log(6, VERBOSITY, 'key is mandatory: {}'.format(key))
            if not in_dict[key]:
                _log(6, VERBOSITY, key)
                missing.append(key)
    return missing


def process_chore_form(res):
    """convert chore form to Dict and find missing keys"""
    ret_dict = _convert_form_keys(res, CHORE_ATTRS)
    missing = _validate_form_keys(ret_dict, MANDATORY_CHORE_KEYS)
    print('in: {}'.format(res))
    print('ret: {}'.format(ret_dict))
    print('missing: {}'.format(missing))
    return ret_dict, missing

        
def process_reward_form(res):
    """convert reward form to Dict and find missing keys"""
    ret_dict = _convert_form_keys(res, REWARD_ATTRS)
    missing = _validate_form_keys(ret_dict, MANDATORY_REWARD_KEYS)
    return ret_dict, missing


def process_user_form(res):
    """convert user form to Dict and find missing keys"""
    ret_dict = _convert_form_keys(res, USER_ATTRS)
    missing = _validate_form_keys(ret_dict, MANDATORY_USER_KEYS)
    ret_dict['full'] = '{} {}'.format(ret_dict['first'], ret_dict['last'])
    print('in: {}'.format(res))
    print('ret: {}'.format(ret_dict))
    print('missing: {}'.format(missing))
    return ret_dict, missing

def verify_user(name=None):
    list_of_users = os.listdir('user_storage')
    print('all users: {}'.format(list_of_users))
    for u in list_of_users:
        if name in u:
            return True
    return False
