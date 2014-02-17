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
  # Send
  server = smtplib.SMTP('smtp.gmail.com:587')
  server.starttls()
  server.login(username,password)
  server.sendmail(username, recipients, msg.as_string())
  server.quit()

def queryOnline(url):
  success = False
  try:
    result = urllib2.urlopen(url).read().strip()
  except urllib2.HTTPError as e:
    result = 'HTTP {0} {1}'.format(e.code, e.reason)
  except urllib2.URLError as e:
    result = 'URLError: {0}'.format(e.reason,)
  except Exception as e:
    result = str(e)
  else:
    success = True
  return (success, result)

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
logtemplatelong = logtemplate + '''  ==>  {2}'''
logging.basicConfig(filename = logFile, level = logLevel, format = FORMAT)
# display logging information in console.
console = logging.StreamHandler(sys.stdout)
console.setLevel(consoleLogLevel)
console.setFormatter(logging.Formatter(FORMAT))
logging.getLogger('').addHandler(console)

# Get IP Address
(success, IPresult) = queryOnline(config.get('publicIP','url'))
if 'Errno 8' in IPresult:  # If strange 'error 8', then retry it once more.
  logging.error('[Public IP] {0}'.format(IPresult))
  (success, IPresult) = queryOnline(config.get('publicIP','url'))
if success == False:     # If not success, log error...
  logging.error('[Public IP] {0}'.format(IPresult))
elif IPresult == '209.114.127.125':  # If using VPN, Do not update anything...
  logging.debug(logtemplate.format('Using VPN, skipping:', IPresult))
  print logtemplate.format('Using VPN, skipping:', IPresult)
else:   
  # We got the current IP!
  currentIP = IPresult;
  logging.debug(logtemplate.format('Current IP address is:', currentIP))
  
  # Read Previous IP from ipFile
  if os.path.exists(ipFile):
    f = open(ipFile,'r')
    previousIP = f.read().strip()
    f.close()
  else:
    previousIP = 'IP file not found'
  logging.debug(logtemplate.format('Previous IP as recorded:', previousIP))

  # See if IP changed...
  if previousIP == currentIP:
    logging.debug(logtemplate.format('IP address not changed:', currentIP))
    print logtemplate.format('IP address not changed:', currentIP)
  else:
    logging.debug(logtemplatelong.format('IP changed:',previousIP, currentIP))
    print logtemplatelong.format('IP changed:',previousIP, currentIP)
    
    # Update FreeDNS with current IP...
    (success, freeDNSresult) = queryOnline(config.get('freeDNS','url'))
    if 'Updated' in freeDNSresult or 'has not changed' in freeDNSresult:
      logging.info('[FreeDNS] {0}'.format(freeDNSresult))
      print '[FreeDNS] {0}'.format(freeDNSresult)
      # Update IP file:
      f = open(ipFile,'w')
      f.write(currentIP)
      f.close()
      # Let the admins know by email
      emailadmin('[FreeDNS] {0}'.format(freeDNSresult))
      logging.debug('Notification email sent out to admins.')
    else:
      logging.error('[FreeDNS] {0}'.format(freeDNSresult))
