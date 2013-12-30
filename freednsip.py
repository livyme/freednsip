#!/usr/bin/env python
# 
#  freednsip.py
#  freednsip
#  
#  Created by Livy on 2013-12-23.
#  Copyright 2013 Livy. All rights reserved.
#  
import smtplib
from email.mime.text import MIMEText
import urllib2
import os.path
import sys
from os import sep
import logging
import ConfigParser

ipFile = sys.path[0]+sep+'ip.txt'
logFile = sys.path[0]+sep+'freednsip.log'

# Reading from setting.cfg file
config = ConfigParser.RawConfigParser()
config.read(sys.path[0]+sep+'settings.cfg')

# Set up logging
logLevel = config.get('logging', 'logLevel')
consoleLogLevel = config.get('logging', 'consoleLogLevel')
FORMAT = '%(asctime)s | %(levelname)-7s | %(message)s'
logging.basicConfig(filename = logFile, level = logLevel, format = FORMAT)
console = logging.StreamHandler(sys.stdout)
console.setLevel(consoleLogLevel)
console.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger('').addHandler(console)

def emailadmin(mesg):
    # Prepare message
    recipients = ['7854326040@txt.att.net', 'i@livyme.com']
    msg = MIMEText(mesg)
    msg['From'] = 'root'
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = config.get('me','name') + ' IP Change'
    # Get gmail account info.
    username = config.get('gmail','username')
    password = config.get('gmail','password')
    # Mail send using alert
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(username, recipients, msg.as_string())
    server.quit()

def updatedns(ip):
    code = False
    try:
        conn = urllib2.urlopen(config.get('freeDNS','url'))
        result = conn.read().strip()
        if 'Updated' in result or 'has not changed' in result:
            f = open(ipFile,'w')
            f.write(ip)
            f.close()
            code = True
        else:
            result = 'While changing DNS: Unknow error: {}'.format(result)
    except urllib2.HTTPError as e:
        result = 'While changing DNS: HTTP {}: {}'.format(e.code, e.reason)
    except urllib2.URLError as e:
        result = 'While changing DNS: URLError: {} ==> Is the Internet down?'.format(e.reason)
    except Exception as e:
        result = 'While changing DNS: Error: {}'.format(e)
    return(code, result)
    
try:
    # Get IP Address
    currentIP = urllib2.urlopen(config.get('publicIP','url')).read().strip()
    logging.debug('%-22s\t%s', 'Current IP address is:', currentIP)
    # Read previously recorded IP from ipFile
    if os.path.exists(ipFile):
        f = open(ipFile,'r')    
        previousIP = f.read().strip()
        f.close()
    else:
        previousIP = 'IP file not found'
        
    logging.debug('%-22s\t%s','Previous IP as recorded:', previousIP)

    if previousIP == currentIP:
        logging.info('IP address %s not changed.', currentIP)
    else:
        logging.info('%-22s ==>\t%s', 'IP changed: ' +  previousIP, currentIP)
        (code, result) = updatedns(currentIP)
        if code:
            logging.info(result)
            emailadmin(result)
            logging.debug('Notification email sent out to admins.')
        else:
            logging.error(result)
except urllib2.HTTPError as e:
    logging.error('While checking IP: HTTP {}: {}'.format(e.code, e.reason))
except urllib2.URLError as e:
    logging.error('While checking IP: URLError: {} ==> Is the Internet down?'.format(e.reason))
except Exception as e:
    logging.error('While checking IP: Error: {}'.format(e))