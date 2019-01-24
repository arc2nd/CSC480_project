import types
import datetime
import os
import json
import calendar

basedir = os.path.dirname(os.path.realpath(__file__))

""" Environment Configuration """
def get_now():
    return calendar.timegm(datetime.datetime.now().timetuple())

def get_creds(path, crypt=False):
    path = os.path.join(basedir, path)
    if os.path.exists(path):
        with open(path, 'r') as fp: 
            j = json.load(fp)
        return j