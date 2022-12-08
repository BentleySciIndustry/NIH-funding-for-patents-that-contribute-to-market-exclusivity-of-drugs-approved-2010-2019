#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 21:54:43 2021

@author: MAAT
"""
import os
import smtplib 

EMAIL_ADDRESS = os.environ.get('maatzeng0507@gmail.com')
EMAIL_PASSWORD = os.environ.get('xcuzwvdigiwmgwmx')


with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    
    smtp.login("maatzeng0507@gmail.com", "xcuzwvdigiwmgwmx")
    
    subject = "Python EMAIL"
    body = "HAHAHHAHAHHAHAH "
    
    msg = f'Subject: {subject} \n\n {body}'
    
    smtp.sendmail("maatzeng0507@gmail.com", "xliu@falcon.bentley.edu", msg)
    