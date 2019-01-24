#!/usr/bin/env python
#Log.py
import os
import datetime
import time
from enum import Enum

class LogType(Enum):
    INFO = 0
    WARN = 1
    ERROR = 2

class Log():
    logFile = '.log'
    logPath = '.\\src\\logs\\'

    def __init__(self, log_file = logFile, log_path = logPath):
        self.logFile = log_file
        self.logPath = log_path

    @classmethod
    def log(cls, msg, msgType=None):
        if not msgType:
            msgType = LogType.INFO
        else:
            msgType = msgType

        logpath = os.path.join(cls.logPath, msgType.name.lower() + cls.logFile)

        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        logFormatted = '[{0}] {1} - {2}\n'.format(ts, msgType.name, msg)

        if msgType == LogType.ERROR:
            print(logFormatted)

        if os.path.exists(logpath):
            with open(logpath, 'a') as fp:
                fp.write(logFormatted)
        else:
            with open(logpath, 'w') as fp:
                fp.write(logFormatted)

