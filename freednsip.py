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
import time
from email.mime.text import MIMEText

ipFile = '/usr/local/freednsip/ip.txt'
freeDNSHost = 'freedns.afraid.org'
mbpFreeDNSString = 'VURmdmdhMzFVMVVBQU9IVVN5MEFBQUFIOjg0NDc2ODg='
centralFreeDNSString = 'VURmdmdhMzFVMVVBQU9IVVN5MEFBQUFIOjgyMDY3NTc='
dnsURL = '/dynamic/update.php?'+ mbpFreeDNSString
selfName = 'Macbook Pro Retina'

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
    
def updatedns(ip):
    # Change FreeDNS registration
    print 'Updating DNS...'
    while True:
        conn = httplib.HTTPConnection(freeDNSHost)
        conn.request('GET', dnsURL)
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
            print 'Got resonse from server: ', result, '\n Retry after 20 sec...'
            time.sleep(20)

try:
    # Get IP Address
    currentIP = urllib2.urlopen("http://ip.dnsexit.com/").read().strip()
    print '\n\nCurrent IP address is:\t\t', currentIP
    # Read previously recorded IP from ipFile
    if not os.path.exists(ipFile):
        print 'Previous IP as recorded:\tFile not found'
        updatedns(currentIP)
    else:
        f = open(ipFile,'r')    
        previousIP = f.read()
        f.close()
        print 'Previous IP as recorded:\t', previousIP
        if previousIP == currentIP:
            print 'IP not changed.\n\n'
        else:
            print 'IP change detected.'
            updatedns(currentIP)
except Exception as e:
    print 'Error:\n',e