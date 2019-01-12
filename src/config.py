import types
import datetime
import os
import json
import calendar

basedir = os.path.abspath(os.path.dirname(__file__))

""" Environment Configuration """

def get_now():
    return calendar.timegm(datetime.datetime.now().timetuple())

def get_creds(path, crypt=False):
    if crypt:
        # this section must be replaced with a more cross-platform encrypt/decrypt function
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



#class Config(object):
	#SECRET_KEY = "thisisnotasecret"
	#CSRF_ENABLED = True
	#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
