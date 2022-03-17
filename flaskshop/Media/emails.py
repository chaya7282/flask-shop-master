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
