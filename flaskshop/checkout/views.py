from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required
from pluggy import HookimplMarker

from .models import CartLine, Cart, ShippingMethod
from .forms import NoteForm, VoucherForm, CheckoutForm, PaymentDeliveryForm
from flaskshop.account.forms import AddressForm
from flaskshop.account.models import UserAddress
from flaskshop.utils import flash_errors
from flaskshop.order.models import Order
from flaskshop.discount.models import Voucher


impl = HookimplMarker("flaskshop")


def cart_index():

    shipping_methods = ShippingMethod.query.all()

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
        cart = Cart.get_current_user_cart()
        shipping_method = ShippingMethod.get_by_id(request.form["shipping_method"])
        payment_method = request.form["payment_method"]

        cart.update(
            shipping_method_id=shipping_method.id,
            payment_method=payment_method
        )

    return redirect(url_for("checkout.shipment_details"))




def shipment_details():

    addresses = current_user.addresses
    if addresses:
        form = AddressForm(obj=addresses)
    else:
        form =AddressForm()
    if request.method == "POST":
        cart = Cart.get_current_user_cart()

        form.populate_obj(cart)
        address_data = {
        "user_id": current_user.id,
        "province": form.province.data,
        "city": form.city.data,
        "district": form.district.data,
        "address": form.address.data,
        "contact_name": form.contact_name.data,
        "contact_phone": form.contact_phone.data,
        "pincode": form.pincode.data,
        "email":form.email.data
        }
        if addresses:
            form.populate_obj(addresses)
            flash("Success edit address.", "success")
        else:
            UserAddress.create(**address_data)
            flash("Success add address.", "success")
        user_address = current_user.addresses
        cart.update( shipping_address_id=user_address.id)
        order, msg = Order.create_whole_order(cart)
        if order:
            return render_template(
                "checkout/order_placed.html", order=order
            )

        else:
            flash(msg, "warning")
            return render_template("errors/out_of_stock.html")

    return render_template(
        "checkout/check_out.html", form=form
    )




def checkout_shipping():

    addresses = current_user.addresses
    if addresses:
       user_address = addresses[0]
       form = CheckoutForm(obj=user_address)
    else:
        form = CheckoutForm()
    if request.method == "POST":
        if request.form["address_sel"] != "new":
            user_address = UserAddress.get_by_id(request.form["address_sel"])
        elif request.form["address_sel"] == "new" and form.validate_on_submit():
            user_address = UserAddress.create(
                province=form.province.data,
                city=form.city.data,
                district=form.district.data,
                address=form.address.data,
                contact_name=form.contact_name.data,
                contact_phone=form.contact_phone.data,
                user_id=current_user.id,
            )
        shipping_method = ShippingMethod.get_by_id(request.form["shipping_method"])

        if user_address and shipping_method:
            cart = Cart.get_current_user_cart()
            cart.update(
                shipping_address_id=user_address.id,
                shipping_method_id=shipping_method.id,
            )
            return redirect(url_for("checkout.checkout_note"))
    flash_errors(form)
    shipping_methods = ShippingMethod.query.all()
    return render_template(
        "checkout/check_out.html", form=form, shipping_methods=shipping_methods
    )


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
        order, msg = Order.create_whole_order(cart, form.note.data)
        if order:
            return redirect(order.get_absolute_url())
        else:
            flash(msg, "warning")
            return redirect(url_for("checkout.cart_index"))
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

    app.register_blueprint(bp, url_prefix="/checkout")
