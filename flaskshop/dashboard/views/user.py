from flask import render_template, redirect, url_for, request,flash
from sqlalchemy import or_

from flaskshop.account.models import User, UserAddress
from flaskshop.order.models import Order
from flaskshop.dashboard.forms import UserForm, UserAddressForm


def users():
    page = request.args.get("page", type=int, default=1)
    search_word = request.args.get("keyword")
    query = User.query
    if search_word:
        query = query.filter(
            or_(
                User.username.like("%" + search_word + "%"),
                User.email.like("%" + search_word + "%"),
            )
        )
    pagination = query.paginate(page, 10)
    props = {
        "id": "ID",
        "username": "Username",
        "email": "Email",
        "is_active_human": "Is Active",
    }
    context = {
        "title": "User List",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
    }
    return render_template("user/list.html", **context)


def user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash("user does not  exist")
        return render_template("errors/user_doesnt_exsist.html")

    address = user.addresses
    orders = Order.get_user_orders(user_id)
    roles = user.roles
    context = {"user": user, "address": address, "orders": orders, "roles":roles}
    return render_template("user/detail.html", **context)


def user_edit(user_id):
    user = User.get_by_id(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        if not form.password.data:
            del form.password
        form.populate_obj(user)
        new_role_id= int(form.role.data)
        user.add_a_role(new_role_id)
        return redirect(url_for("dashboard.user", user_id=user_id))
    roles = user.roles
    return render_template("user/edit.html", form=form, roles=roles)


def address_edit(id):
    addr = UserAddress.get_by_id(id)
    form = UserAddressForm(obj=addr)
    if form.validate_on_submit():
        form.populate_obj(addr)
        addr.save()
        return redirect(url_for("dashboard.user", user_id=addr.user_id))
    return render_template("user/edit_addr.html", form=form)

def user_del(user_id):
    user = User.get_by_id(user_id)
    if user:
        user.delete()
    return redirect(url_for("dashboard.users"))