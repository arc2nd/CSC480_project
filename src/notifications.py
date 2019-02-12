#!/usr/bin/env python

# To start a python debugging SMTP server:
# python -m smtpd -n -c DebuggingServer localhost:1025


import Chore
import User
import Reward
import SystemValues
import smtplib
import os
import config
from Log import Log, LogType
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl

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

def send_reward_claim_notice(reward=None, user=None, debug=True):
    claim_text_path = os.path.join(basedir, 'reward_claim_text.txt')
    claim_html_path = os.path.join(basedir, 'reward_claim_html.txt')
    if reward and user:
        to_email = user.email_address
        admin_email = User.User.GetByUsername('administrator').email_address
        from_email = 'cxp@ChoreExplore.com'

        # get and prep the email text and html
        with open(claim_text_path, 'r') as fp:
            text = fp.read()
        with open(claim_html_path, 'r') as fp:
            html = fp.read()
        text = text.replace('%THIS_USER%', user.username)
        html = html.replace('%THIS_USER%', user.username)
        text = text.replace('%REWARD_NAME%', reward.name)
        html = html.replace('%REWARD_NAME%', reward.name)

        # build the email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'ChoreExplore Reward Claimed'
        msg['From'] = from_email
        msg['to'] = to_email # , admin_email]

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        print('admin: {}'.format(admin_email))
        print('user: {}'.format(to_email))

        if debug:
            send_debug_email(to_list=[to_email, admin_email], from_email=from_email, msg=msg)
        else:
            send_email2(to_list=[to_email, admin_email], from_email=from_email, msg=msg)
    return

def send_debug_email(to_list, from_email, msg):
    server = smtplib.SMTP('localhost', 1025)
    server.sendmail(from_email, to_list, msg.as_string())
    server.quit()

def send_email(to_list, from_email, msg):
    # for using a gmail account
    port = 465  # For SSL
    password = raw_input("Type your password and press enter: ")

    # Create a secure SSL context
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 425, context=context)
    server.login('fake_account@gmail.com', password)
    server.sendmail(from_email, [to_email, admin_email], msg.as_string())
    server.quit()


def send_email2(to_list, from_email, msg):
    import smtplib, ssl

    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    password = raw_input("Type your password and press enter: ")

    # Create a secure SSL context
    context = ssl.create_default_context()

    server = None
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls() # context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(from_email, password)
        server.sendmail(from_email, to_list, msg.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        if server:
            server.quit()


def send_reminder(chore=None, debug=True):
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
        if debug:
            send_debug_email(to_list=[to_email, admin_email], from_email=from_email, msg=msg)
        else:
            send_email2(to_list=[to_email, admin_email], from_email=from_email, msg=msg)
    return
            
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
    
