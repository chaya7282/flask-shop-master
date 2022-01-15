# -*- coding: utf-8 -*-
"""Product views."""
from flask import Blueprint, render_template, request, jsonify,redirect,url_for
from flask_login import login_required
from pluggy import HookimplMarker

from flaskshop.checkout.models import Cart

from .models import Product, Category, ProductCollection, ProductVariant
from .forms import AddCartForm
from flaskshop.constant import Language

impl = HookimplMarker("flaskshop")


def show(id, form=None):
    product = Product.get_by_id(id)
    if not form:
        form = AddCartForm(request.form, product=product)
    return render_template("products/single_product_view.html", product=product, form=form)





@login_required
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

    Cart.add_to_currentuser_cart(int(quantity), int(variant_id))

    return redirect(url_for("public.home"))


def variant_price(id):
    variant = ProductVariant.get_by_id(id)
    return jsonify({"price": float(variant.price), "stock": variant.stock})


def show_category(id):
    page = request.args.get("page", 1, type=int)
    ctx = {}
    print("product--")
    query=Product.query.filter_by(category_id= id)
    print("product--")
    pagination = query.paginate(page, per_page=10)
    print(" pagination--")
    category= Category.query.filter_by(id=id)
    categories = Category.query.all()
    ctx.update(object=category, pagination=pagination, products=pagination.items,categories=  categories, Language= Language)

    return render_template("category/index.html", **ctx)


def show_collection(id):
    page = request.args.get("page", 1, type=int)
    ctx = ProductCollection.get_product_by_collection(id, page)
    return render_template("category/index.html", **ctx)

def product_search():
    keyword = request.form['keyword']
    searchResult = Product.query.filter(Product.title.contains(keyword)).all()

    return render_template("search/index.html",title='Searching..' + keyword,products=searchResult,Language= Language)

@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("product", __name__)
    bp.add_url_rule("/<int:id>", view_func=show)
    bp.add_url_rule("/api/variant_price/<int:id>", view_func=variant_price)
    bp.add_url_rule("/<int:id>/add", view_func=product_add_to_cart, methods=["POST"])
    bp.add_url_rule("/category/<int:id>", view_func=show_category)
    bp.add_url_rule("/collection/<int:id>", view_func=show_collection)
    bp.add_url_rule("/search", view_func=product_search, methods=["POST"])
    app.register_blueprint(bp, url_prefix="/products")
