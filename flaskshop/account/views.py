# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from pluggy import HookimplMarker

from .forms import AddressForm, LoginForm, RegisterForm, ChangePasswordForm
from .models import UserAddress, User
from flaskshop.product.models import Category
from flaskshop.utils import flash_errors
from flaskshop.order.models import Order

impl = HookimplMarker("flaskshop")

def user_orders():
    orders = Order.get_current_user_orders()
    categories = Category.query.all()
    return render_template("account/dashboard_my_orders.html", orders=orders )


def index():

    form = ChangePasswordForm(request.form)
    orders = Order.get_current_user_orders()
    categories = Category.query.all()
    return render_template("account/details.html", form=form, orders=orders)

def index_by_user(user_id):
    form = ChangePasswordForm(request.form)
    orders = Order.get_current_user_orders()
    categories = Category.query.all()
    return render_template("account/details.html", form=form,  orders=orders)

def login():
    """login page."""
    form = LoginForm(request.form)
    categories = Category.query.all()
    if form.validate_on_submit():
        login_user(form.user)

        return redirect(url_for("public.home"))

    else:
        flash_errors(form)
    return render_template("account/sign_in.html", form=form)


@login_required
def logout():
    """Logout."""
    logout_user()

    return redirect(url_for("public.home"))


def signup():
    """Register new user."""
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User.create(
            username=form.username.data,
            email=form.email.data.lower(),
            password=form.password.data,
            is_active=True,
        )
        login_user(user)
        flash("You are signed up.", "success")
        return redirect( url_for('public.home'))
    else:
        flash_errors(form)
    return render_template("account/signup.html", form=form)


def set_password():
    form = ChangePasswordForm(request.form)
    categories = Category.query.all()
    if request.method == "POST":
        if form.validate_on_submit():
            current_user.update(password=form.password.data)
            flash("You have changed password.", "success")
            return redirect(url_for("account.index") )
        else:
            flash("You have not changed password.", "failure")
    return render_template("account/forgot_password.html", form=form)


def addresses():
    """List addresses."""
    categories = Category.query.all()
    addresses = current_user.addresses
    return render_template("account/dashboard_my_addresses.html", addresses=addresses)


def edit_address():
    """Create and edit an address."""
    categories = Category.query.all()
    form = AddressForm(request.form)
    address_id = current_user.addresses_id
    if address_id:
        user_address = UserAddress.get_by_id(address_id)
        form = AddressForm(request.form, obj=user_address)
    else:
        form.contact_name.data=current_user.username
        form.email.data = current_user.email
    if request.method == "POST" and form.validate_on_submit():
        address_data = {
            "user_id":current_user.id,
            "province": form.province.data,
            "city": form.city.data,
            "district": form.district.data,
            "address": form.address.data,
            "contact_name": form.contact_name.data,
            "contact_phone": form.contact_phone.data,
            "email": form.email.data,
            "pincode": form.pincode.data
        }

        if address_id:
            user_address.update( **address_data)
            flash("Success edit address.", "success")
        else:
            UserAddress.create(**address_data)
            flash("Success add address.", "success")

        return redirect(url_for("public.home"))

    return render_template("account/address_edit.html", form=form, address_id=address_id,show_cart=False)


def delete_address(id):
    user_address = UserAddress.get_by_id(id)
    if user_address in current_user.addresses:
        UserAddress.delete(user_address)
    return redirect(url_for("account.index") + "#addresses")


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("account", __name__)
    bp.add_url_rule("/", view_func=index)
    bp.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
    bp.add_url_rule("/logout", view_func=logout)
    bp.add_url_rule("/signup", view_func=signup, methods=["GET", "POST"])
    bp.add_url_rule("/set_password", view_func=set_password, methods=["GET", "POST"])
    bp.add_url_rule("/address", view_func=addresses)
    bp.add_url_rule("/address/edit", view_func=edit_address, methods=["GET", "POST"])
    bp.add_url_rule(
        "/user_orders", view_func=user_orders)
    bp.add_url_rule(
        "/address/<int:id>/delete", view_func=delete_address, methods=["POST"]
    )
    user_orders
    app.register_blueprint(bp, url_prefix="/account")
