# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, render_template, request, send_from_directory
from sqlalchemy.sql import or_
import os
from pluggy import HookimplMarker
from flaskshop import settings

from flaskshop.extensions import login_manager
from flaskshop.account.models import User
from flaskshop.product.models import Product, Category
from .models import Page
from .search import Item
from datetime import datetime, date, timedelta
from twilio.rest import Client
import smtplib

import numpy as np
import random
from flaskshop.product.forms import AddCartForm
impl = HookimplMarker("flaskshop")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


def home():
    products = Product.query.all()
    init_time = datetime.now()
    msg_time = init_time + timedelta(seconds=59)
    account_sid = 'ACed43da2e3a902ae5a72f5c22b8b0ac55'
    auth_token = '3cf059ad933a35352c56e54f0ad4ed16'
    client = Client(account_sid, auth_token)

    message = client.messages.create(from_ ="+17252158551",to='+972524534533', body='zz' )

    print(message.sid)

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    MIME-Version: 1.0
    Content-type: text/html
    Subject: SMTP HTML e-mail test

    This is an e-mail message to be sent in HTML format

    <b>This is HTML message.</b>
    <h1>This is headline.</h1>
    """
    sender = 'from@fromdomain.com'
    receivers = ['chaya.zilberstein@gmail.com']

    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receivers, message)


    return render_template("public/index.html", products= products)


def style():
    return render_template("public/style_guide.html")


def favicon():
    return send_from_directory("static", "favicon-32x32.png")


def search():
    query = request.args.get("q", "")
    page = request.args.get("page", default=1, type=int)
    pagination = Item.new_search(query, page)
    return render_template(
        "public/search_result.html",
        products=pagination.items,
        query=query,
        pagination=pagination,
    )


def show_page(identity):
    page = Page.get_by_identity(identity)
    return render_template("public/page.html", page=page)


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("public", __name__)
    bp.add_url_rule("/", view_func=home)
    bp.add_url_rule("/style", view_func=style)
    bp.add_url_rule("/favicon.ico", view_func=favicon)
    bp.add_url_rule("/search", view_func=search)
    bp.add_url_rule("/page/<identity>", view_func=show_page)
    app.register_blueprint(bp)
