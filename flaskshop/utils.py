# -*- coding: utf-8 -*-

"""Helper utilities and decorators."""

import logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import get_debug_queries
from flask import flash, request, current_app
from urllib.parse import urlencode
from flaskshop.product.models import Category
from flaskshop.public.models import MenuItem
from flaskshop.checkout.models import Cart,ShippingMethod

from flaskshop.dashboard.models import Setting
from flaskshop.plugin.utils import template_hook
from flaskshop.constant import SiteDefaultSettings
from flaskshop.create_menus import create_menus
from flaskshop.constant import Language
from flaskshop.account.models import Business

def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {error}", category)


def log_slow_queries(app):
    formatter = logging.Formatter(
        "[%(asctime)s]{%(pathname)s:%(lineno)d}\n%(levelname)s - %(message)s"
    )
    handler = RotatingFileHandler(
        "slow_queries.log", maxBytes=10_000_000, backupCount=10
    )
    handler.setLevel(logging.WARN)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    @app.after_request
    def after_request(response):
        for query in get_debug_queries():
            if query.duration >= app.config["DATABASE_QUERY_TIMEOUT"]:
                app.logger.warn(
                    f"Context: {query.context}\n"
                    f"SLOW QUERY: {query.statement}\n"
                    f"Parameters: {query.parameters}\n"
                    f"Duration: {query.duration}"
                )
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Expires'] = '0'
        response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        return response


def jinja_global_varibles(app):
    """Register global varibles for jinja2"""



    @app.context_processor
    def inject_cart():
        current_user_cart = Cart.get_current_user_cart()
        return dict(current_user_cart=current_user_cart)

    @app.context_processor
    def inject_Language():
        return dict(Language=Language)

    @app.context_processor
    def inject_shipping_methods():
        shipping_methods = ShippingMethod.query.all()
        return dict(shipping_methods=shipping_methods)

    @app.context_processor
    def inject_business():
        business = Business.query.first()
        return dict(business=business)

    @app.context_processor
    def inject_categories():
        categories = Category.query.all()
        return dict(categories=categories)

    @app.context_processor
    def inject_menus():

        return dict(top_menu=None, bottom_menu=None)

    @app.context_processor
    def inject_site_setting():
        settings = {}
        for key, value in SiteDefaultSettings.items():

            obj = Setting.query.filter_by(key=key).first()
            if not obj:
                obj = Setting.create(key=key, **value)

            settings[key] = obj
        return dict(settings=settings)

    def get_sort_by_url(field, descending=False):
        request_get = request.args.copy()
        if descending:
            request_get["sort_by"] = "-" + field
        else:
            request_get["sort_by"] = field
        return f"{request.path}?{urlencode(request_get)}"

    app.add_template_global(current_app, "current_app")
    app.add_template_global(get_sort_by_url, "get_sort_by_url")
    app.add_template_global(template_hook, "run_hook")
