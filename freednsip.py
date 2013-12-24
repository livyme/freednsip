#!/usr/bin/env python
# 
#  freednsip.py
#  freednsip
#  
#  Created by Livy on 2013-12-23.
#  Copyright 2013 Livy. All rights reserved.
#  
# 
import httplib
import smtplib
import time
from email.mime.text import MIMEText

ipFile = '/usr/local/freednsip/ip.txt'
freeDNSHost = 'freedns.afraid.org'
mbpFreeDNSString = 'VURmdmdhMzFVMVVBQU9IVVN5MEFBQUFIOjg0NDc2ODg='
centralFreeDNSString = 'VURmdmdhMzFVMVVBQU9IVVN5MEFBQUFIOjgyMDY3NTc='
dnsURL = '/dynamic/update.php?'+ mbpFreeDNSString
selfName = 'Macbook Pro Retina'

# Get IP Address
try:
    conn = httplib.HTTPConnection('ipecho.net')
    conn.request('GET', '/plain')
    r1 = conn.getresponse()
    # print 'status: ', r1.status
    # print 'reason: ', r1.reason
    currentIP = r1.read()
    conn.close()
    # Read previously recorded IP from ipFile
    # If file not exists then create it.
    try:
        f = open(ipFile,'r')
    except IOError:
        print ('no ip file exsits, creating it')
        f = open(ipFile,'w+')
    
    previousIP = f.read()
    f.close()

    if previousIP == currentIP:
        print 'IP not changed, nothing to do. \nCurrent IP is', currentIP
    else:
        print 'IP changed to ', currentIP
    
        # Change FreeDNS registration
        while True:
            conn = httplib.HTTPConnection(freeDNSHost)
            conn.request('GET', dnsURL)
            r1 = conn.getresponse()
            result = r1.read()
            conn.close()
            
            if r1.status == 200:
                if 'Updated' in result:
                    f = open(ipFile,'w')
                    f.write(currentIP)
                    f.close()
                    print 'Update dns successful\n',result
                elif 'has not changed' in result:
                    print result
                    # Although no change, but go ahead and change the IP file anyway
                    f = open(ipFile,'w')
                    f.write(currentIP)
                    f.close()
                else:
                    print 'Unknown error\n',result
                break
            else:
                print 'Got resonse from server: ', result, '\n Retry after 20 sec...'
                time.sleep(20)

        # Send notifications if ip changes...
        # Prepare message
        recipients = ['7854326040@txt.att.net', 'i@livyme.com']
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
        print 'Notification email sent out to admins.'

except Exception as e:
    print e