import types
import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

""" Environment Configuration """

class Config(object):
	SECRET_KEY = "thisisnotasecret"
	CSRF_ENABLED = True
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']