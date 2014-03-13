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
import ConfigParser

def email_admin(mesg):
  recipients = ['i@livyme.com',]
  msg = MIMEText(mesg)
  msg['From'] = 'root'
  msg['To'] = ', '.join(recipients)
  msg['Subject'] = config.get('me', 'name') + ' IP Change'
  username = config.get('gmail', 'username')
  password = config.get('gmail', 'password')
  server = smtplib.SMTP('smtp.gmail.com:587')
  server.starttls()
  server.login(username, password)
  server.sendmail(username, recipients, msg.as_string())
  server.quit()

def query_online(url):
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

# Reading from setting.cfg file
config = ConfigParser.RawConfigParser()
config.read(sys.path[0]+sep+'settings.cfg')

# Get IP Address
(success, current_ip) = query_online(config.get('publicIP','url'))
if not success:     
  sys.stderr.write('[Public IP] {0}'.format(IPresult))
elif current_ip != '209.114.127.125':  # Do not update when using FHSU VPN
  if os.path.exists(ipFile):
    f = open(ipFile,'r')
    previous_ip = f.read().strip()
    f.close()
  else:
    previous_ip = 'IP file not found'

  if previous_ip != current_ip:
    (success, free_dns_result) = query_online(config.get('freeDNS','url'))
    if 'Updated' in free_dns_result or 'has not changed' in free_dns_result:
      f = open(ipFile,'w')
      f.write(current_ip)
      f.close()
      # Let the admins know by email
      email_admin('[FreeDNS] {0}'.format(free_dns_result))
    else:
      sys.stderr.write('[FreeDNS] {0}'.format(free_dns_result))