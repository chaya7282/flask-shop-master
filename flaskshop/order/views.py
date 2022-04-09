import time
from datetime import datetime
from flaskshop.Media.emails import send_receipt
from flaskshop.account.models import Business
from flask import Flask, render_template, jsonify, request, redirect, Blueprint
from flaskshop.order.models import ShippingAddress,  Shipping_time_date
from flask import flash, abort
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    current_app,
    url_for,
    abort,
)
from flask_login import login_required, current_user
from pluggy import HookimplMarker

from .models import Order, OrderPayment,UserAddress
from flaskshop.product.models import Category

from .payment import zhifubao
from flaskshop.extensions import csrf_protect
from flaskshop.constant import ShipStatusKinds, PaymentStatusKinds, OrderStatusKinds
import paypalrestsdk
from flaskshop.checkout.models import Cart
impl = HookimplMarker("flaskshop")


@login_required
def index():
    return redirect(url_for("account.index"))


@login_required
def show(token):
    order = Order.query.filter_by(token=token).first()
    user_id = order.user_id
    user_address= None
    if  user_id:
        user_address = UserAddress.query.filter_by(user_id= user_id ).first()

    return render_template("checkout/order_placed.html", order = order,user_address= user_address )


def create_payment(token, payment_method):
    order = Order.query.filter_by(token=token).first()
    if order.status != OrderStatusKinds.unfulfilled.value:
        abort(403, "This Order Can Not Pay")
    payment_no = str(int(time.time())) + str(current_user.id)
    customer_ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    payment = OrderPayment.query.filter_by(order_id=order.id).first()
    if payment:
        payment.update(
            payment_method=payment_method,
            payment_no=payment_no,
            customer_ip_address=customer_ip_address,
        )
    else:
        payment = OrderPayment.create(
            order_id=order.id,
            payment_method=payment_method,
            payment_no=payment_no,
            status=PaymentStatusKinds.waiting.value,
            total=order.total,
            customer_ip_address=customer_ip_address,
        )
    if payment_method == "alipay":
        order_string = zhifubao.send_order(order.token, payment_no, order.total)
        payment.order_string = order_string
    return payment


@login_required
def ali_pay(token):
    payment = create_payment(token, "alipay")
    return redirect(current_app.config["PURCHASE_URI"] + payment.order_string)


@csrf_protect.exempt
def ali_notify():
    data = request.form.to_dict()
    signature = data.pop("sign")
    success = zhifubao.verify_order(data, signature)
    if success:
        order_payment = OrderPayment.query.filter_by(
            payment_no=data["out_trade_no"]
        ).first()
        order_payment.pay_success(paid_at=data["gmt_payment"])
    return "", 200


# for test pay flow
@login_required
def test_pay(token):
    payment = create_payment(token, "testpay")
    payment.pay_success(paid_at=datetime.now())
    redirect(url_for('dashboard.orders'))


@login_required
def payment_success():
    return render_template("orders/checkout_success.html")


@login_required
def cancel_order(token):
    order = Order.query.filter_by(token=token).first()
    if not order.is_self_order:
        abort(403, "This is not your order!")
    order.cancel()
    return redirect(url_for('dashboard.order_edit',id=order.id))

@login_required
def receive(token):
    order = Order.query.filter_by(token=token).first()
    order.update(
        status=OrderStatusKinds.completed.value,
        ship_status=ShipStatusKinds.received.value,
    )
    return redirect(url_for('dashboard.order_edit', id=order.id))
@csrf_protect.exempt
def payment():
    print("hell")
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": "AWXiT6_4d9XWj60PtnrwO7RsqKcZ5-hfD6h0jE6NM7_0XSQUWjR8oPP-npFJqaby-AmwPj1wYfac0d78",
        "client_secret": "EPCFDnaorPq44s5oMw52OaxLwbWkINBP1WsSyvdDMqP4SXvDNL502cdhgVRXH87t0RqwNT5ozxVn5qCn"})

    cart = Cart.get_current_user_cart()

    items= cart.pay_pal_items()
    payment_arguments = {
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal'
        },
        'redirect_urls': {
            'return_url': url_for('order.execute'),

            'cancel_url': url_for('order.cancel')
        },
        'transactions': [{
            'item_list': {
                'items': items
            },
            'amount': {
                'total': str(cart.total),
                'currency': "ILS"
            },
            'description': 'Make sure to include'
        }]
    }
    payment = paypalrestsdk.Payment( payment_arguments)

    if payment.create():
        cart.paymentID = payment.id
        cart.save()
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID': payment.id})

@csrf_protect.exempt
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])
    cart= Cart.query.filter_by(paymentID=payment.id).first()
    if payment.execute({'payer_id' : request.form['payerID']}):
        order, msg = Order.create_whole_order(cart)
        order.paymentID=payment.id
        order.save()
        success = True
        print("execution sucess")
    else:
        flash("Sorry, Payment was not acceptes.", "failure")
        print('Execute error!')
    return jsonify(success)
@csrf_protect.exempt
def cancel():
    payment = paypalrestsdk.Payment.find(request.form['paymentID'])
    order = Order.query.filter_by(paymentID=payment.id).all()
    print("got here")
    if order:
        order.delete()
    return True

@csrf_protect.exempt
def create_reception(paymentID):
    address_id = current_user.addresses_id
    user_address = None
    if address_id:
        user_address = UserAddress.get_by_id(address_id)

    order = Order.query.filter_by(paymentID=paymentID).first()
    if order:
        shippment_address = ShippingAddress.get_by_id(order.shipping_address_id)
        html = render_template("checkout/order_placed_template.html", order=order, user_address=shippment_address)

        business = Business.query.first()
        send_receipt(mail_to=shippment_address.email, title='Thanks for buying from ' + business.name, html=html)
        send_receipt(mail_to=business.email, title='Order number' + order.token, html=html)

        return render_template("checkout/order_placed.html", order=order, user_address=shippment_address)
    else:

        return render_template("errors/out_of_stock.html", )
@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("order", __name__)
    bp.add_url_rule("/", view_func=index)
    bp.add_url_rule("/orders/<string:token>", view_func=show)
    bp.add_url_rule("/pay/<string:token>/alipay", view_func=ali_pay)
    bp.add_url_rule("/alipay/notify", view_func=ali_notify, methods=["POST"])
    bp.add_url_rule("/pay/<string:token>/testpay", view_func=test_pay)
    bp.add_url_rule("/payment_success", view_func=payment_success)

    bp.add_url_rule("/cancel/<string:token>", view_func=cancel_order)
    bp.add_url_rule("/receive/<string:token>", view_func=receive)
    bp.add_url_rule("/payment", view_func=payment, methods=["POST"])
    bp.add_url_rule("/execute", view_func=execute, methods=["POST"])
    bp.add_url_rule("/create_reception/<string:paymentID>", view_func=create_reception, methods=["POST","GET"])

    bp.add_url_rule("/cancel", view_func=cancel, methods=["POST"])
    app.register_blueprint(bp, url_prefix="/orders")
