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
from flaskshop.extensions import mail
from flaskshop.constant import SiteDefaultSettings

from flaskshop.product.models import Product, Category

impl = HookimplMarker("flaskshop")
from flask import  current_app

def cart_index():

    shipping_methods = ShippingMethod.query.all()
    categories = Category.query.all()
    return render_template("checkout/cart.html",shipping_methods=shipping_methods)


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

def Cart_Checkout():

    if request.method == "POST":

        shipping_method = ShippingMethod.get_by_id(request.form["shipping_method"])
        payment_method = request.form["payment_method"]
        cart = Cart.get_current_user_cart()
        for line in cart.lines:
            qty = request.form.get(f"qty_{line.id}")
            line.quantity = int(qty)


            line.save()
        cart.update(
            shipping_method_id=shipping_method.id,
            payment_method=payment_method
        )
    return redirect(url_for("checkout.step_1_delivery_address"))



def Create_An_Order(address_data):
    cart = Cart.get_current_user_cart()
    address_id = current_user.addresses_id
    user_address= None
    if address_id:
        user_address = UserAddress.get_by_id(address_id)

    order, msg = Order.create_whole_order(cart, shippment_address=address_data)

    if order:

        return render_template("checkout/order_placed.html", order=order,user_address=user_address)
    else:
        flash(msg, "warning")
        return render_template("errors/out_of_stock.html")


def shipment_details():
    address_data = {}
    if  current_user.addresses:
        address_data = {
            "province": current_user.addresses.province,
            "city": current_user.addresses.city,
            "district": current_user.addresses.district,
            "address": current_user.addresses.address,
            "contact_name": current_user.addresses.contact_name,
            "contact_phone": current_user.addresses.contact_phone,
            "pincode": current_user.addresses.pincode,
            "email": current_user.addresses.email
        }

def step_1_delivery_address():
    form = AddressForm(request.form)
    address_id = current_user.addresses_id
    cart = Cart.get_current_user_cart()
    if address_id:
        user_address = UserAddress.get_by_id(address_id)
        form = AddressForm(request.form, obj=user_address)
    if request.method == "POST" and form.validate_on_submit():
        shippment_address = {

            "province": form.province.data,
            "city": form.city.data,
            "district": form.district.data,
            "address": form.address.data,
            "contact_name": form.contact_name.data,
            "contact_phone": form.contact_phone.data,
            "email": form.email.data,
            "pincode": form.pincode.data
        }
        shipping_address = ShippingAddress.create(**shippment_address)
        cart.shipping_address_id = shipping_address.id
        cart.save()
        return redirect(url_for("checkout.delivery_time_date"))

    return render_template("checkout/step-delivery_address.html", form=form, address_id=address_id, show_cart=True)


def get_Shipping_address():
    form = AddressForm(request.form)
    address_id = current_user.addresses_id
    if address_id:
        user_address = UserAddress.get_by_id(address_id)
        form = AddressForm(request.form, obj=user_address)
    if request.method == "POST" and form.validate_on_submit():
        address_data = {

            "province": form.province.data,
            "city": form.city.data,
            "district": form.district.data,
            "address": form.address.data,
            "contact_name": form.contact_name.data,
            "contact_phone": form.contact_phone.data,
            "email": form.email.data,
            "pincode": form.pincode.data
        }
        return redirect(url_for("checkout.delivery_time_date"))

    return render_template("checkout/step-delivery_address.html", form=form, address_id=address_id,show_cart=True)

def delivery_time_date():
    cart = Cart.get_current_user_cart()
    if request.method == "POST":
        day = request.form["address1"]
        hours= request.form["fruit"]
        cart.Shipping_time_date= day+hours
        cart.save()
        return redirect(url_for("checkout.payment_details"))
    else:
        return render_template("checkout/delivery_time_date.html")


def payment_details():
    cart = Cart.get_current_user_cart()

    if request.method == "POST":

        if cart.shipping_method_id == "Credit Card":
             holdername= request.form["holdername"]
             cardnumber= request.form["cardnumber"]
             expiremonth = request.form["card[expire-month]"]
             expireyear = request.form["card[expire-year]"]
             cvc= request.form["card[cvc]"]
        shippment_address= ShippingAddress.get_by_id(cart.shipping_address_id)

        order, msg = Order.create_whole_order(cart,shipping_address=shippment_address)

        if order:

            return render_template("checkout/order_placed.html", order=order, user_address=shippment_address)
        else:
            flash(msg, "warning")
            return render_template("errors/out_of_stock.html", )

    return render_template("checkout/payment_details.html", paymentmethod=cart.payment_method )


def checkout_shipping():

    user_address = current_user.addresses[0]

    shipping_method = ShippingMethod.get_by_id(request.form["shipping_method"])

    if user_address and shipping_method:
        cart = Cart.get_current_user_cart()
        cart.update(
            shipping_address_id=user_address.id,
            shipping_method_id=shipping_method.id,
        )
    return redirect(url_for("checkout.checkout_note"))




def checkout_note():
    form = NoteForm(request.form)
    voucher_form = VoucherForm(request.form)
    cart = Cart.get_current_user_cart()

    address = (
        UserAddress.get_by_id(cart.shipping_address_id)
        if cart.shipping_address_id
        else None
    )
    shipping_method = (
        ShippingMethod.get_by_id(cart.shipping_method_id)
        if cart.shipping_method_id
        else None
    )
    if form.validate_on_submit():
        order, msg = Order.create_whole_order(cart,shippment_address=address, )
        if not order:
            flash(msg, "warning")
        else:
            return render_template("checkout/order_placed.html", order=order, Language=Language)

    return render_template(
        "checkout/note.html",
        form=form,
        address=address,
        voucher_form=voucher_form,
        shipping_method=shipping_method,


    )


def checkout_voucher():
    voucher_form = VoucherForm(request.form)
    if voucher_form.validate_on_submit():
        voucher = Voucher.get_by_code(voucher_form.code.data)
        cart = Cart.get_current_user_cart()
        err_msg = None
        if voucher:
            try:
                voucher.check_available(cart)
            except Exception as e:
                err_msg = str(e)
        else:
            err_msg = "Your code is not correct"
        if err_msg:
            flash(err_msg, "warning")
        else:
            cart.voucher_code = voucher.code
            cart.save()
        return redirect(url_for("checkout.checkout_note"))


def checkout_voucher_remove():
    voucher_form = VoucherForm(request.form)
    if voucher_form.validate_on_submit():
        cart = Cart.get_current_user_cart()
        cart.voucher_code = None
        cart.save()
        return redirect(url_for("checkout.checkout_note"))


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
    bp.add_url_rule("/details", view_func=shipment_details, methods=["GET", "POST"])
    bp.add_url_rule("/shipping", view_func=checkout_shipping, methods=["GET", "POST"])
    bp.add_url_rule("/note", view_func=checkout_note, methods=["GET", "POST"])
    bp.add_url_rule("/delivery_type", view_func=Cart_Checkout, methods=["POST"])
    bp.add_url_rule("/voucher", view_func=checkout_voucher, methods=["POST"])
    bp.add_url_rule(
        "/voucher/remove", view_func=checkout_voucher_remove, methods=["POST"]
    )
    bp.add_url_rule(
        "/get_Shipping_address", view_func=get_Shipping_address, methods=["GET", "POST"])
    bp.add_url_rule(
        "/delivery_time_date", view_func=delivery_time_date, methods=["GET", "POST"])
    bp.add_url_rule(
        "/step_1_delivery_address", view_func=step_1_delivery_address, methods=["GET", "POST"])
    bp.add_url_rule("/payment_details", view_func= payment_details, methods=["GET", "POST"])


    app.register_blueprint(bp, url_prefix="/checkout")
