import types
import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))


""" Environment Configuration """

class Config(object):
	SECRET_KEY = "thisisnotasecret"
	CSRF_ENABLED = True
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


USER_ATTRS = {'name': str, 
              'email': str, 
              'first': str, 
              'last': str, 
              'middle': str, 
              'full': str, 
              'dob': datetime, 
              'points': float,  
              'type': str, 
              'style': str, 
              'timeout': int, 
              'pw_hash': str, 
              'id': int
             }

CHORE_ATTRS = {'name': str, 
               'desc': str, 
               'due': datetime, 
               'expired': bool, 
               'points': float, 
               'creator': str, 
               'assigned_to': str, 
               'done': datetime, 
               'id': int
               }

REWARD_ATTRS = {'name': str,
                'desc': str, 
                'due': datetime, 
                'expired': bool, 
                'points': float,  
                'creator': str, 
                'assigned_to': str, 
                'claimed': bool, 
                'recurring': str, 
                'id': int
               }
