from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required
from pluggy import HookimplMarker
from flaskshop.order.models import ShippingAddress,  Shipping_time_date
from .models import CartLine, Cart, ShippingMethod
from .forms import NoteForm, VoucherForm, CheckoutForm, PaymentDeliveryForm
from flaskshop.account.forms import AddressForm
from flaskshop.account.models import UserAddress
from flaskshop.utils import flash_errors
from flaskshop.order.models import Order
from flaskshop.discount.models import Voucher
from flask_mail import Message
from flaskshop.settings import Config
from flaskshop.Media.emails import send_receipt
from flaskshop.extensions import mail
from flaskshop.constant import SiteDefaultSettings
import paypalrestsdk
from flaskshop.product.models import Product, Category
from flaskshop.account.models import Business
from flaskshop.extensions import csrf_protect
impl = HookimplMarker("flaskshop")
from flask import  current_app
from flaskshop.constant import OrderStatusKinds


def cart_index():

    shipping_methods = ShippingMethod.query.all()
    categories = Category.query.all()
    return render_template("checkout/cart.html",shipping_methods=shipping_methods)

@login_required
def update_cart(id):
    # TODO when not enough stock, response ajax error
    line = CartLine.get_by_id(id)

    response = {
        "variantId": line.variant_id,
        "subtotal": 0,
        "total": 0,
        "cart": {"numItems": 0, "numLines": 0},
    }

    if request.form["quantity_"] == "0":
        line.delete()
    else:
        line.quantity = int(request.form["quantity_"])
        line.save()
    cart = Cart.query.filter(Cart.user_id == current_user.id).first()

    response["cart"]["numItems"] = cart.update_quantity()
    response["cart"]["numLines"] = len(cart)
    response["subtotal"] = "$" + str(line.subtotal)
    response["total"] = "$" + str(cart.total)
    jsonify(response)
    return redirect(url_for("checkout.cart_index"))

@login_required
def Cart_Checkout():

    if request.method == "POST":

        shipping_method = ShippingMethod.get_by_id(request.form["shipping_method"])
        payment_method = request.form["payment_method"]
        cart = Cart.get_current_user_cart()

        cart.update(
            shipping_method_id=shipping_method.id,
            payment_method=payment_method
        )

        for line in cart.lines:
            qty = request.form.get(f"qty_{line.id}")
            line.quantity = int(qty)
            line.save()
        cart.clean_lines()
        cart.update_quantity()

        next_operation= request.form["submitom"]

        if cart and next_operation == "checkout":

            order, msg = Order.create_whole_order(cart)
            order.paymentStatus = OrderStatusKinds.unfulfilled.value
            order.status='unfulfilled'
            current_user.order_id = order.id
            order.save()
            current_user.save()
            cart.delete()
            return redirect(url_for("checkout.step_1_delivery_address"))
        else:
            return redirect(url_for("public.home"))




@login_required
def step_1_delivery_address():
    order = Order.get_by_id(current_user.order_id)
    form = AddressForm(request.form)
    address_id = current_user.addresses_id

    if address_id:
        user_address = UserAddress.get_by_id(address_id)
        form = AddressForm(request.form, obj=user_address)
    else:
        form.contact_name.data = current_user.username
        form.email.data = current_user.email
        form.contact_phone.data=current_user.contact_phone

    if request.method == "POST" and form.validate_on_submit():
        shippment_address = {

            "province": form.province.data,
            "city": form.city.data,
            "district": form.district.data,
            "address": form.address.data,
            "contact_name": form.contact_name.data,
            "contact_phone": form.contact_phone.data,
            "email": form.email.data,
            "company_name": form.company_name.data
        }
        shipping_address = ShippingAddress.create(**shippment_address)
        order.shipping_address_id = shipping_address.id
        order.set_contact()
        order.save()
        return redirect(url_for("checkout.payment_details"))

    return render_template("checkout/step-delivery_address.html", form=form, address_id=address_id)



@login_required

def delivery_time_date():
    order = Order.get_by_id(current_user.order_id)
    if request.method == "POST":
        day = request.form["address1"]
        hours= request.form["fruit"]
        order.shipping_time_date= day+hours
        order.save()
        return redirect(url_for("checkout.payment_details"))
    else:
        return render_template("checkout/delivery_time_date.html")


def payment_details():
    order = Order.get_by_id(current_user.order_id)

    return render_template("checkout/payment_details.html", paymentmethod=order.payment_method )

















@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("checkout", __name__)

    @bp.before_request
    @login_required
    def before_request():
        """The whole blueprint need to login first"""
        pass

    bp.add_url_rule("/cart", view_func=cart_index)
    bp.add_url_rule(
        "/update_cart/<int:id>", view_func=update_cart, methods=["POST"]
    )


    bp.add_url_rule("/delivery_type", view_func=Cart_Checkout, methods=["POST"])

    bp.add_url_rule(
        "/delivery_time_date", view_func=delivery_time_date, methods=["GET", "POST"])
    bp.add_url_rule(
        "/step_1_delivery_address", view_func=step_1_delivery_address, methods=["GET", "POST"])
    bp.add_url_rule("/payment_details", view_func= payment_details, methods=["GET", "POST"])

    app.register_blueprint(bp, url_prefix="/checkout")
