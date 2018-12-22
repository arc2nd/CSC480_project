#!/usr/bin/env python
#Helpers.py
#this is a good spot to put functions that don't really fit other descriptions

import datetime

import config
from Log import _log

MANDATORY_CHORE_KEYS = ['name']
OPTIONAL_CHORE_KEYS= ['points', 'desc', 'due']
POSSIBLE_CHORE_KEYS = MANDATORY_CHORE_KEYS + OPTIONAL_CHORE_KEYS

MANDATORY_REWARD_KEYS = ['name', 'points']
OPTIONAL_REWARD_KEYS = ['desc', 'expires']
POSSIBLE_REWARD_KEYS = MANDATORY_REWARD_KEYS + OPTIONAL_REWARD_KEYS

MANDATORY_USER_KEYS = ['name', 'email', 'type']
OPTIONAL_USER_KEYS = ['first', 'middle', 'last', 'dob', 'style']
POSSIBLE_USER_KEYS = MANDATORY_USER_KEYS + OPTIONAL_USER_KEYS

VERBOSITY = 1

CHORE_ATTRS = config.CHORE_ATTRS

def _convert_form_keys(in_dict):
    """Converts an ImmutableDict to a regular Dict
       and converts type if necessary
    """
    ret_dict = {}
    for key in in_dict:
        if 'submit' not in key.lower():
            val = in_dict[key]
            if not isinstance(val, CHORE_ATTRS[key]):
                if isinstance('string', CHORE_ATTRS[key]):
                    val = '{}'.format(val)
                if isinstance(0.0, CHORE_ATTRS[key]):
                    val = float(val)
                if isinstance(1, CHORE_ATTRS[key]):
                    val = int(val)
                if isinstance(datetime.datetime.now(), CHORE_ATTRS[key]):
                    val = _convert_str_to_dt(val)
            ret_dict[key] = val
        else:
            _log(6, VERBOSITY, 'submit', 'chore.log')
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


def _process_chore_form(res):
    """convert chore form to Dict and find missing keys"""
    ret_dict = _convert_form_keys(res)
    missing = _validate_form_keys(ret_dict, MANDATORY_CHORE_KEYS)
    return ret_dict, missing

        
def _process_reward_form(res):
    """convert reward form to Dict and find missing keys"""
    ret_dict = _convert_form_keys(res)
    missing = _validate_form_keys(ret_dict, MANDATORY_REWARD_KEYS)
    return ret_dict, missing


def _process_user_form(res):
    """convert user form to Dict and find missing keys"""
    ret_dict = _convert_form_keys(res)
    missing = _validate_form_keys(ret_dict, MANDATORY_USER_KEYS)
    return ret_dict, missing


