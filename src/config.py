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
    ret_dict = { 
                "ADMIN_ROLE_ID": 0,
				"SECRET_KEY": "I am a secret key", 
                "CSRF_ENABLED": True, 
                "SQLALCHEMY_DATABASE_URI": "postgresql://cxp:choresarereallyfun@localhost/ChoreExplore", 
                "SQLALCHEMY_TRACK_MODIFICATIONS": False, 
                "WTF_CSRF_SECRET_KEY": "this-needs-to-change-in-production"
               }
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