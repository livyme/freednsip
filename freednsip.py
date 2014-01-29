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

def emailadmin(mesg):
  # Prepare message
  recipients = ['i@livyme.com',]
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
  success = False
  try:
    conn = urllib2.urlopen(config.get('freeDNS','url'))
  except urllib2.HTTPError as e:
    result = 'HTTP {} {}'.format(e.code, e.reason)
  except urllib2.URLError as e:
    result = 'URLError: {} ==> Is the Internet down?'.format(e.reason,)
  except Exception as e:
    result = 'Error: {}'.format(str(e))
  else:
    result = conn.read().strip()
    if 'Updated' in result or 'has not changed' in result:
      f = open(ipFile,'w')
      f.write(ip)
      f.close()
      success = True
    else:
      result = 'Unknow error: {}'.format(result)
  result = '[FreeDNS] {}'.format(result)
  return(success, result)

ipFile = sys.path[0]+sep+'ip.txt'
logFile = sys.path[0]+sep+'freednsip.log'

# Reading from setting.cfg file
config = ConfigParser.RawConfigParser()
config.read(sys.path[0]+sep+'settings.cfg')

# Set up logging
logLevel = config.get('logging', 'logLevel')
consoleLogLevel = config.get('logging', 'consoleLogLevel')
FORMAT = '%(asctime)s | %(levelname)-7s | %(message)s'
logtemplate = '''{0:<22s}\t{1:>15s}'''
logging.basicConfig(filename = logFile, level = logLevel, format = FORMAT)
# display logging information in console.
console = logging.StreamHandler(sys.stdout)
console.setLevel(consoleLogLevel)
console.setFormatter(logging.Formatter(FORMAT))
logging.getLogger('').addHandler(console)

# Get IP Address
try:
  currentIP = urllib2.urlopen(config.get('publicIP','url')).read().strip()
except urllib2.HTTPError as e:
  logging.error('[Public IP] HTTP {} {}'.format(e.code, e.reason))
except urllib2.URLError as e:
  logging.error('[Public IP] URLError: {}'.format(e.reason,))
else:
  # If using VPN, Do not update anything...
  if currentIP == '209.114.127.125':
    logging.debug(logtemplate.format('Using VPN, skipping:', currentIP))
    print logtemplate.format('Using VPN, skipping:', currentIP)
  else:
    logging.debug(logtemplate.format('Current IP address is:', currentIP))
    # Read previously recorded IP from ipFile
    if os.path.exists(ipFile):
      f = open(ipFile,'r')
      previousIP = f.read().strip()
      f.close()
    else:
      previousIP = 'IP file not found'
    logging.debug(logtemplate.format('Previous IP as recorded:', previousIP))

    if previousIP == currentIP:
      logging.debug(logtemplate.format('IP address not changed:', currentIP))
      print logtemplate.format('IP address not changed:', currentIP)
    else:
      logging.debug('{0:<22s}\t{1:>15s}  ==>  {2}'.format('IP changed:',previousIP, currentIP))
      print '{0:<22s}\t{1:>15s}  ==>  {2}'.format('IP changed:',previousIP, currentIP)
      (success, result) = updatedns(currentIP)
      if success:
        logging.info(result)
        print result
        emailadmin(result)
        logging.debug('Notification email sent out to admins.')
      else:
        logging.error(result)