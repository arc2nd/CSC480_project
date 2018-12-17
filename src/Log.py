#!/usr/bin/env python
#Log.py
import os

def _log(priority, verbosity, msg, logpath=None):
    if verbosity >= priority:
        print(msg)
        if logpath:
            if os.path.exists(logpath):
                with open(logpath, 'a') as fp:
                    fp.write(msg)
                    fp.write('\n')
            else:
                with open(logpath, 'w') as fp:
                    fp.write(msg)
                    fp.write('\n')
