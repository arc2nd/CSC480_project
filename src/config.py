import types
import datetime
import os
import json
import calendar

basedir = os.path.dirname(os.path.realpath(__file__))

""" Environment Configuration """

def get_base_directory():
    print(basedir)
    return basedir

def get_now():
    return calendar.timegm(datetime.datetime.now().timetuple())

def get_creds(path, crypt=False):
    ret_dict = { 
                "SECRET_KEY": "I am a default secret key",
                "CSRF_ENABLED": True, 
                "SQLALCHEMY_DATABASE_URI": "postgresql://cxp:choresarereallyfun@localhost/ChoreExplore", 
                "SQLALCHEMY_TRACK_MODIFICATIONS": False, 
                "WTF_CSRF_SECRET_KEY": "this-needs-to-change-in-production"
               }
    if crypt:
        import my_crypto as mc
        if os.path.exists(path):
            ret_dict = mc.decrypt_from_file(path)
        return ret_dict
    else:
        path = os.path.join(basedir, path)
        if os.path.exists(path):
            try:
                with open(path, 'r') as fp: 
                    j = json.load(fp)
                return j
            except:
                return ret_dict


#class Config(object):
#	SECRET_KEY = "thisisnotasecret"
#	CSRF_ENABLED = True
#	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
