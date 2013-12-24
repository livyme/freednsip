#!/usr/bin/env python
# 
#  freednsip.py
#  freednsip
#  
#  Created by Livy on 2013-12-23.
#  Copyright 2013 Livy. All rights reserved.
#  

import subprocess
import smtplib
import time
from email.mime.text import MIMEText

ipFile = '/usr/local/freednsip/ip.txt'
mbpFreeDNSString = 'VURmdmdhMzFVMVVBQU9IVVN5MEFBQUFIOjg0NDc2ODg='
centralFreeDNSString = 'VURmdmdhMzFVMVVBQU9IVVN5MEFBQUFIOjgyMDY3NTc='
dnsURL = 'http://freedns.afraid.org/dynamic/update.php?'+ mbpFreeDNSString
selfName = 'Macbook Pro Retina'

# Get IP Address
currentIP = subprocess.check_output(['curl', '--silent', 'http://ipecho.net/plain'])

# Read IP from ip.txt, if not exists then create it.
try:
    f = open(ipFile,'r')
except IOError:
    print ('no ip file exsits, creating it')
    subprocess.call(['touch', ipFile])
    f = open(ipFile,'r')
previousIP = f.read()
f.close()

if previousIP == currentIP:
    print 'IP not changed, nothing to do. \nCurrent IP is', currentIP
else:
    print 'IP changed to ', currentIP
    
    # Change FreeDNS registration
    # subprocess.call(['curl', '-k', '--silent', dnsURL])
    
    # Some weird error occurs when contacting FreeDNS server.
    # So when receiving a 502 bad gateway error
    
    while True:
        proc = subprocess.Popen(['curl', '-k', '--silent', dnsURL], stdout=subprocess.PIPE)
        (out,err) = proc.communicate()
        
        if 'Updated' in out:
            f = open(ipFile,'w')
            f.write(currentIP)
            f.close()
            print 'Update dns successful'
            break
        elif 'has not changed' in out:
            print 'Address in DNS does not appear to have changed.'
            break
        elif '502 Bad Gateway' in out:
            print '502 Bad Gateway code, retry after 20 seconds...'
            time.sleep(20)
        else:
            print 'Unknown error'
            break
    
    # Send notifications if ip changes...
    # Prepare message
    recipients = ['7854326040@txt.att.net', 'i@livyme.com', 'li.livy@gmail.com']
    msg = MIMEText('Public IP address for '+ selfName +' has changed. \nNew IP: ' + currentIP)
    msg['From'] = 'root'
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = selfName + ' IP Change'
    # Optional header fields just for fun
    msg['X-Priority'] = '1'
    msg['X-Message-Flag'] = 'Livyme'
    msg['X-Generated-By'] = 'Python'
    msg['Importance'] = 'High'
    
    ## Send out using sendmail
    ## p = subprocess.Popen(["/usr/sbin/sendmail", "-t"], stdin=subprocess.PIPE)
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
    print 'Notification email sent out to admins.'