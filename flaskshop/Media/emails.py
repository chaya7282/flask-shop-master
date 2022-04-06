from flaskshop.extensions import mail
from flask_mail import Message
from flaskshop.account.models import Business
from flask import  current_app

import os
from flaskshop.settings import Config
def send_receipt(mail_to, title,html):

    msg = Message(title,
                  sender=current_app.config["MAIL_USERNAME"], recipients=[mail_to])
    msg.html=html

    try:
        mail.send(msg)
    except Exception as inst:
       print("not set")

def send_sms(account_sid ,auth_token ,message, to):
    account_sid = 'ACed43da2e3a902ae5a72f5c22b8b0ac55'
    auth_token = '3cf059ad933a35352c56e54f0ad4ed16'
  #  client = Client(account_sid, auth_token)

   # message = client.messages.create(from_="+17252158551", to='+972524534533', body='zz')

  #  print(message.sid)