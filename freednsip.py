#!/usr/bin/env python
# 
#  freednsip.py
#  freednsip
#  
#  Created by Livy on 2013-12-23.
#  Copyright 2013 Livy. All rights reserved.
#  
import httplib
import smtplib
import urllib2
import os.path
import sys
from os import sep
import logging
import time
import ConfigParser
from email.mime.text import MIMEText

# Reading from setting.cfg file
config = ConfigParser.RawConfigParser()
config.read(sys.path[0]+sep+'settings.cfg')
ipFile = sys.path[0]+sep+'ip.txt'
logFile = sys.path[0]+sep+'freednsip.log'

logLevel = config.get('logging', 'logLevel')
consoleLogLevel = config.get('logging', 'consoleLogLevel')

# Setting up logging
FORMAT = '%(asctime)s | %(levelname)-7s | %(message)s'
logging.basicConfig(filename=logFile, level=logLevel, format=FORMAT)
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
    msg['Subject'] = config.get('settings','selfName') + ' IP Change'
    # Optional header fields just for fun
    msg['X-Priority'] = '1'
    msg['X-Message-Flag'] = 'Livyme'
    msg['X-Generated-By'] = 'Python'
    msg['Importance'] = 'High'
    # Get gmail account info.
    username = config.get('gmail','username')
    password = config.get('gmail','password')
    # Mail send using alert
    fromAddr = 'alert@livyme.com'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromAddr, recipients, msg.as_string())
    server.quit()
    logging.debug('Notification email sent out to admins.')

def updatedns(ip):
    freeDNSHost = config.get('settings','freeDNSHost')
    freeDNSURL = config.get('settings','freeDNSURL')
    while True:
        conn = httplib.HTTPConnection(freeDNSHost)
        conn.request('GET', freeDNSURL)
        r1 = conn.getresponse()
        result = r1.read()
        conn.close()
        if r1.status == 200:
            if 'Updated' in result:
                f = open(ipFile,'w')
                f.write(ip)
                f.close()
            elif 'has not changed' in result:
                # Although no change, but go ahead and change the IP file anyway
                f = open(ipFile,'w')
                f.write(ip)
                f.close()
            else:
                logging.warning ('Unknow error')
            logging.debug('From FreeDNS:')
            logging.info(result.strip())
            break
        else:
            logging.error('HTTP response code: {0}'.format(r1.status))
            logging.error('HTTP response content:\n' + result)
            logging.error('Retry after 20 sec...')
            time.sleep(20)
    return result.strip()
    
try:
    # Get IP Address
    currentIP = urllib2.urlopen('http://ip.dnsexit.com/').read().strip()
    logging.debug('%-22s\t%s', 'Current IP address is:', currentIP)
    # Read previously recorded IP from ipFile
    if not os.path.exists(ipFile):
        previousIP = 'IP file not found'
    else:
        f = open(ipFile,'r')    
        previousIP = f.read().strip()
        f.close()
    logging.debug('%-22s\t%s','Previous IP as recorded:', previousIP)
    # If ip not changed, then do nothing.
    if previousIP == currentIP:
        logging.info('IP address %s not changed.', currentIP)
    else:
        logging.info('%-22s ==>\t%s', 'IP changed: ' +  previousIP, currentIP)
        emailadmin(updatedns(currentIP))
except Exception as e:
    logging.error('{0} ==> Is the Internet down?'.format(e.reason))