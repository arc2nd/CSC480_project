#!/usr/bin/env python

import Chore
import User
import SystemValues
import smtplib
import os
import config
from Log import Log, LogType
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_log = Log()

basedir = os.path.dirname(os.path.realpath(__file__)) 

CONFIG = config.get_creds('envs.json', crypt=False)

def notifications_enabled():
    system_value_notifications = CONFIG['SYSTEM_VALUES_NOTIFICATIONS']
    notifications_enabled = (SystemValues.SystemValues.GetById(system_value_notifications)).value_bool
    return notifications_enabled

def check_due():
    overdue_list = []
    all_chores = Chore.Chore.GetAll()
    for c in all_chores:
        if c.IsOverdue():
            overdue_list.append(c)
    return overdue_list

def send_reminder(chore=None):
    reminder_text_path = os.path.join(basedir, 'reminder_text.txt')
    reminder_html_path = os.path.join(basedir, 'reminder_html.txt')
    if chore:
        # get the assigned user, if none, send to the admin
        if chore.assigned_to:
            this_user = User.User.GetById(chore.assigned_to)
        else:
            this_user = User.User.GetById(1)
        to_email = this_user.email_address
        from_email = 'cxp@ChoreExplore.com'

        # get and prep the email text and html
        with open(reminder_text_path, 'r') as fp:
            text = fp.read()
        with open(reminder_html_path, 'r') as fp:
            html = fp.read()
        text = text.replace('%CHORE_NAME%', chore.name)
        html = html.replace('%CHORE_NAME%', chore.name)

        # build the email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'ChoreExplore Reminder'
        msg['From'] = from_email
        msg['To'] = to_email

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        # send the email message
        s = smtplib.SMTP('localhost', 1025)
        s.sendmail(from_email, [to_email], msg.as_string())
        s.quit()
            
if __name__ == '__main__':
    notifications_status = False
    notifications_status = notifications_enabled()

    _log.log('Notifications status: {0}'.format(notifications_status), LogType.INFO)

    if notifications_status:
        print('Sending notifications')
        all_overdue = check_due()
        for c in all_overdue:
            send_reminder(chore=c) 
    else:
        print('Notifications not enabled.')
