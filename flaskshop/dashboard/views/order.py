from datetime import datetime

from flask import request, render_template, redirect,url_for
from sqlalchemy import and_, or_, not_
from flaskshop.order.models import Order
from flaskshop.constant import OrderStatusKinds
from flaskshop.dashboard.forms import OrderStatusForm

def search_Orders():
    query = Order.query.order_by(Order.id.desc())
    search_word= request.form["search_order"]

    return redirect(url_for("public.home"))

def orders(query=None):
    page = request.args.get("page", type=int, default=1)
    if not query:
        query = Order.query.order_by(Order.id.desc())
    pagination = query.paginate(page, 10)


    props = {
        "id": "ID",
        "identity": "Identity",
        "status_human": "Status",
        "total_human": "Total",
        "user": "User",
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
    form = OrderStatusForm()
    if form.validate_on_submit():
        status = form.status.data
        if status == OrderStatusKinds.canceled.value:
            order.cancel()
        elif  status == OrderStatusKinds.completed.value:
             order.complete()
        elif  status == OrderStatusKinds.shipped.value:
            order.delivered()
        return redirect(url_for('dashboard.orders'))

    return render_template("order/order_edit.html",form=form, order=order,order_stats_kinds=OrderStatusKinds )


def order_detail(id):
    order = Order.get_by_id(id)
    return render_template("order/order_view.html", order=order)


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