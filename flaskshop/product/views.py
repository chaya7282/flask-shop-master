# -*- coding: utf-8 -*-
"""Product views."""
from flask import Blueprint, render_template, request, jsonify,redirect,url_for
from flask_login import login_required
from pluggy import HookimplMarker

from flaskshop.checkout.models import Cart

from .models import Product, Category, ProductCollection, ProductVariant
from .forms import AddCartForm
from flask_login import current_user

impl = HookimplMarker("flaskshop")


def show(id):
    product = Product.query.filter_by(id=id).first()

    ctx={}
    print("product--")
    pagination = None
    print(" pagination--")
    category = Category.query.filter_by(id=product.category_id).first()

    ctx.update(object=category, pagination=pagination, products=[product])

    return render_template("products/product_list_base.html",**ctx)


def show_single(id):
    product = Product.query.filter_by(id=id).first()

    return render_template("products/single_product_view.html",product=product)


def product_add_to_cart(id):
    """ this method return to the show method and use a form instance for display validater errors"""

    product = Product.get_by_id(id)
    quantity=request.form["id_quantity"]

    attribute_list={}
    for variant_attributes in product.product_type.variant_attributes:
        value= request.form[variant_attributes.title]
        attribute_list[str(variant_attributes.id)]=value

    if product.has_variants:
        variant = ProductVariant.search_varint_by_attributs(attribute_list,product.id)
        variant_id = variant.id
    else:
        variant_id = product.variant[0].id

    if current_user.is_authenticated:
        Cart.add_to_currentuser_cart(int(quantity), int(variant_id))
    else:
        return redirect(url_for("account.login"))

    return redirect(url_for("public.home"))




def variant_price(id):
    variant = ProductVariant.get_by_id(id)
    return jsonify({"price": float(variant.price), "stock": variant.stock})


def show_category(id):
    print("product--")

    page = request.args.get("page", type=int,default=1)


    ctx = {}

    query=Product.query.filter_by(category_id= id)

    pagination = query.paginate(page, per_page=10)

    category= Category.query.filter_by(id=id).first()

    ctx.update(object=category, pagination=pagination, products=pagination.items)

    return render_template("category/index.html", **ctx)

def show_on_sale():
    page = request.args.get("page", type=int,default=1)
    ctx = {}
    query=Product.query.filter_by(on_sale=True)
    pagination = query.paginate(page, per_page=10)
    ctx.update(title="on_sale", pagination=pagination, products=pagination.items)
    return render_template("products/special_groups.html", **ctx)
def show_featured():
    page = request.args.get("page", type=int,default=1)
    ctx = {}
    query=Product.query.filter_by(is_featured=True)
    pagination = query.paginate(page, per_page=10)
    ctx.update(title="Featured ", pagination=pagination, products=pagination.items)
    return render_template("products/special_groups.html", **ctx)


def show_collection(id):
    page = request.args.get("page", 1, type=int)
    ctx = ProductCollection.get_product_by_collection(id, page)
    return render_template("category/index.html", **ctx)

def product_search():
    keyword = request.form['keyword']
    searchResult = Product.query.filter(Product.title.contains(keyword)).all()


    ctx = {}
    print("product--")
    pagination =None
    print(" pagination--")
    category =None
    categories = Category.query.all()
    ctx.update(object=category, pagination=pagination, products=searchResult)

    return render_template("products/product_list_base.html", **ctx)



@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("product", __name__)
    bp.add_url_rule("/<int:id>", view_func=show)
    bp.add_url_rule("/<int:id>/show_single", view_func= show_single)
    bp.add_url_rule("/show_on_sale", view_func=show_on_sale)
    bp.add_url_rule("/show_featured", view_func=show_featured)
    bp.add_url_rule("/api/variant_price/<int:id>", view_func=variant_price)
    bp.add_url_rule("/<int:id>/add", view_func=product_add_to_cart, methods=["POST"])
    bp.add_url_rule("/category/<int:id>", view_func=show_category)
    bp.add_url_rule("/collection/<int:id>", view_func=show_collection)
    bp.add_url_rule("/search", view_func=product_search, methods=["POST"])
    app.register_blueprint(bp, url_prefix="/products")
