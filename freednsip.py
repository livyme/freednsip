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
import logging
import time
import ConfigParser
from email.mime.text import MIMEText

config = ConfigParser.RawConfigParser()
config.read('settings.cfg')

freeDNSHost = config.get('settings','freeDNSHost')
freeDNSURL = config.get('settings','freeDNSURL')
ipFile = config.get('settings','ipFile')
logFile = config.get('settings','logFile')
selfName = config.get('settings','selfName')

FORMAT = '%(asctime)s | %(levelname)s  \t| %(message)s'
logging.basicConfig(filename=logFile, level=logging.DEBUG, format=FORMAT)
logging.debug('Begin:')

def emailadmin(mesg):
    # Prepare message
    recipients = ['7854326040@txt.att.net', 'i@livyme.com']
    msg = MIMEText(mesg)
    msg['From'] = 'root'
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = selfName + ' IP Change'
    # Optional header fields just for fun
    msg['X-Priority'] = '1'
    msg['X-Message-Flag'] = 'Livyme'
    msg['X-Generated-By'] = 'Python'
    msg['Importance'] = 'High'
    
    ## Send out using sendmail
    ## p =subprocess.Popen(["/usr/sbin/sendmail", "-t"], stdin=subprocess.PIPE)
    ## p.communicate(msg.as_string())
    
    # Send out using gmail
    # Credentials
    username = 'alert@livyme.com'
    password = 'jae1EGhu'
    
    # Mail send using alert
    fromAddr = 'alert@livyme.com'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromAddr, recipients, msg.as_string())
    server.quit()
    print 'Notification email sent out to admins with the following message:\n',mesg
    logging.warning('Notification email sent out to admins with the following message: '+mesg)

def updatedns(ip):

    # Change FreeDNS registration
    logging.debug('Updating DNS...')
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
                emailadmin(result)
            elif 'has not changed' in result:
                # Although no change, but go ahead and change the IP file anyway
                f = open(ipFile,'w')
                f.write(ip)
                f.close()
                content = 'FreeDNS server returns the following code:\n\n'+result+'\nCurrent IP is '+ip
                emailadmin(content)
            else:
                content = 'Unknown error...\nFreeDNS server returns the following code:\n\n'+result+'\nCurrent IP is '+ip
                emailadmin(content)
            break
        else:
            print 'HTTP response from FreeDNS server: ', r1.status, ':\n', result, '\nRetry after 20 sec...'
            logging.error('HTTP response code: '+r1.status)
            logging.error('HTTP response content:\n'+ result)
            logging.error('Retry after 20 sec...')
            time.sleep(20)
    logging.debug ('Finished DNS update.')

try:
    # Get IP Address
    currentIP = urllib2.urlopen('http://ip.dnsexit.com/').read().strip()
    logging.debug('Current IP address is:\t'+currentIP)
    # Read previously recorded IP from ipFile
    if not os.path.exists(ipFile):
        logging.warning('Previous IP as recorded:\tFile not found')
        updatedns(currentIP)
    else:
        f = open(ipFile,'r')    
        previousIP = f.read()
        f.close()
        logging.debug('Previous IP as recorded:\t' + previousIP)
        if previousIP == currentIP:
            print ('IP not changed.')
            logging.info('IP address ' + currentIP + ' not changed. ')
            logging.debug('End')
        else:
            logging.debug('IP change detected.')
            updatedns(currentIP)
except Exception as e:
    print 'Error:\n',e
    logging.error('Tip: Check internet connection, cannot get public IP. ')
    logging.error(e)