from datetime import datetime

from flask import request, render_template, redirect,url_for
from sqlalchemy import and_, or_, not_
from flaskshop.order.models import Order, ShippingAddress
from flaskshop.constant import OrderStatusKinds, orderProcessing
from flaskshop.dashboard.forms import OrderStatusForm
from flaskshop.account.models import UserAddress

def orders(query=None):
        page = request.args.get("page", type=int, default=1)
        query = Order.query.order_by(Order.id.desc())
        if request.form:
            search_word = request.form["search_order"]
            if search_word:
                query = query.filter(or_(Order.contact_name.like(f"%{search_word}%"), Order.status.like(f"%{search_word}%"),
                                         Order.contact_phone.like(f"%{search_word}%")))

        pagination = query.paginate(page, 10)
        props = {
            "id": "ID",
            "identity": "Identity",
            "status": "status",
            "total_human": "Total",
            "contact_name": "contact",
            "contact_phone": "contact-phone ",
            "created_at": "Created At",

        }
        context = {
            "items": pagination.items,
            "props": props,
            "pagination": pagination,
            "order_stats_kinds": OrderStatusKinds,
        }
        return render_template("order/list.html", **context)

def order_edit(id):
    order = Order.get_by_id(id)
    return redirect(url_for('order.show', token=order.token))


def order_detail(id):
    order = Order.get_by_id(id)
    return redirect(url_for('order.show', token=order.token))


def send_order(id):
    order = Order.get_by_id(id)
    order.delivered()
    return render_template("order/detail.html", order=order)


def draft_order(id):
    order = Order.get_by_id(id)
    order.draft()
    return render_template("order/detail.html", order=order)

def order_del(id):
    order = Order.get_by_id(id)
    if order:
        order.cancel()
    return redirect(url_for('dashboard.orders'))