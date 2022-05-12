from datetime import datetime
from flaskshop.public.models import MenuItem
from flask import request, render_template, redirect, url_for, current_app
from flaskshop import utils
from flaskshop.settings import Config
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
import datetime
import os
import secrets
from werkzeug.utils import secure_filename
from flaskshop.Media.media import load_image, upload_file, get_image_url
from PIL import Image
from sqlalchemy import and_, or_, not_
from PIL import Image
import re
from flaskshop.checkout.models import CartLine, Cart
from flaskshop.product.models import (
    ProductAttribute,
    ProductType,
    Collection,
    Product,
    Category,
    ProductType,
    ProductVariant,
    ProductImage,
    ProductTypeAttributes,
    ProductTypeVariantAttributes
)
from flaskshop.dashboard.forms import (
    AttributeForm,
    CollectionForm,
    CategoryForm,
    ProductTypeForm,
    ProductForm,
    ProductCreateForm,
    VariantForm,
)


def attributes():
    page = request.args.get("page", type=int, default=1)
    pagination = ProductAttribute.query.paginate(page, 10)
    props = {
        "id": "ID",
        "title": "Title",
        "values_label": "Value",
        "types_label": "ProductType",
    }
    context = {
        "title": "Product Attribute",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "attributes",
    }
    return render_template("list.html", **context)

def attributes_del(id=None):
    attr = ProductAttribute.get_by_id(id)
    if attr:
        attr.delete()

    type_attr= ProductTypeAttributes.query.filter_by(product_attribute_id=id).all()
    if type_attr:
        for item in  type_attr:
            type_attr.delete()

    return redirect(url_for("dashboard.attributes"))


def attributes_manage(id=None):
    attr = None
    if id:
        attr = ProductAttribute.get_by_id(id)
        form = AttributeForm(obj=attr)
    else:
        form = AttributeForm()
    if form.validate_on_submit():
        if not id:
            attr = ProductAttribute()
        attr.title = form.title.data
        attr.save()
        keys = form.values.data
        current_values = attr.values
        values = []

        for index in range(len(keys)):
            key = keys[index]
            curr_value = [x for x in attr.values if x.title == key]
            new_image = form.background_imgs.data[index]
            is_active = False
            selected = request.form.getlist('check')

            if key in selected:
                is_active = True

            if new_image:
                image = upload_file(new_image)
            else:
                if curr_value:
                    if curr_value[0].image:
                        image = curr_value[0].image
                else:
                    image = "tmp_file.jpg"
            values.append([image, is_active])

        dictionary = dict(zip(keys, values))

        attr.update_values(dictionary)
        attr.save()
        # update relevant products


        return redirect(url_for("dashboard.attributes"))

    return render_template(
        "product/attribute.html", attribute=attr, form=form,
    )

def collections():
    page = request.args.get("page", type=int, default=1)
    pagination = Collection.query.paginate(page, 10)
    props = {"id": "ID", "title": "Title", "created_at": "Created At"}
    context = {
        "title": "Product Collection",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "collections",
    }
    return render_template("list.html", **context)


def collections_manage(id=None):
    if id:
        collection = Collection.get_by_id(id)
        form = CollectionForm(obj=collection)
    else:
        form = CollectionForm()
    if form.validate_on_submit():
        if not id:
            collection = Collection()
        collection.title = form.title.data
        collection.update_products(form.products.data)
        image = form.bgimg_file.data
        if image:
            filename = secure_filename(form.file.data.filename)
            form.file.data.save('uploads/' + filename)
            filename = secure_filename(form.file.data.filename)
            form.file.data.save('uploads/' + filename)

            background_img = image.filename
            upload_file = current_app.config["UPLOAD_DIR"] / background_img
            upload_file.write_bytes(image.read())
            collection.background_img = (
                current_app.config["UPLOAD_FOLDER"] + "/" + background_img
            )
        collection.save()

        return redirect(url_for("dashboard.collections"))
    products = Product.query.all()
    return render_template("product/collection.html", form=form, products=products)


def categories():
    page = request.args.get("page", type=int, default=1)
    query= Category.query
    if request.form:
        search_word = request.form["search_item"]
        if search_word:
            query = query.filter(or_(Category.title.like(f"%{search_word}%")))

    pagination = query.paginate(page, 10)

    props = {
        "id": "ID",
        "title": "Title",
        "is_active":"is_active",
        "product_number": "product-#",
        "created_at": "Created At",
    }
    context = {
        "title": "Product Category",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "categories",
    }
    return render_template("list.html", **context)


def categories_detail(id):
    category = Category.get_by_id(id)

    return render_template("product/category_view.html", category=category)

def categories_del(id):
    category = Category.get_by_id(id)
    if category:
        category.delete()

    return redirect(url_for('dashboard.categories'))


def categories_manage(id=None):
    image_path = None
    פ=5
    if id:
        category = Category.get_by_id(id)
        form = CategoryForm(obj=category)
        form.current_img.data=category.get_background_img_AWS()
    else:
        form = CategoryForm()
    if form.validate_on_submit():
        if not id:
            category = Category()
        image = form.background_img.data
        form.populate_obj(category)

        if image:
            filename=upload_file(image)
            category.background_img=filename
        category.save()
        return redirect(url_for("dashboard.categories"))
    parents = Category.first_level_items()
    return render_template("product/add_category.html", form=form, parents=parents)

def product_types():
    page = request.args.get("page", type=int, default=1)
    pagination = ProductType.query.paginate(page, 10)
    props = {
        "id": "ID",
        "title": "Title",
        "has_variants": "Has Variants",
        "is_shipping_required": "Is Shipping Required",
        "created_at": "Created At",
    }
    context = {
        "title": "Product Type",
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "product_types",
    }
    return render_template("list.html", **context)


def product_types_manage(id=None):
    if id:
        product_type = ProductType.get_by_id(id)
        form = ProductTypeForm(obj=product_type)
    else:
        form = ProductTypeForm()
    if form.validate_on_submit():
        if not id:
            request.form.getlist('usergroups')
            product_type = ProductType.get_or_create(
                title=form.title.data, is_shipping_required=form.is_shipping_required.data
            )[0]
            product_type.save()
            for attr in form.product_attributes.data:
                ProductTypeAttributes.get_or_create(
                    product_type_id=product_type.id, product_attribute_id=int(attr)
                )
            for attr in form.variant_attributes.data:
                ProductTypeVariantAttributes.get_or_create(
                    product_type_id=product_type.id, product_attribute_id=int(attr)
                )

            product_type.save()

            return  redirect(url_for(
                    "dashboard.product_create_step2",
                    product_type_id=product_type.id
                ))
    attributes = ProductAttribute.query.all()
    return render_template(
        "product/product_type.html", form=form, attributes=attributes
    )


def products():
    page = request.args.get("page", type=int, default=1)
    query = Product.query
    if request.form:
        search_word = request.form["search_product"]
        if search_word:
            query = query.filter(or_(Product.title.like(f"%{search_word}%") ))


    pagination = query.paginate(page,10)
    props = {
        "id": "ID",
        "title": "title",
        "basic_price": "Price",
        "is_active": "is_active",
        "category":"Category"
    }


    context = {
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "categories": Category.query.all(),
        "identity": "product",
    }
    return render_template("product/shop_products.html", **context)


def product_detail(id):
    product = Product.get_by_id(id)
    if not product:
        flash("Product does not  exist")
        return render_template("errors/user_doesnt_exsist.html")

    return render_template("product/product_view.html", product=product)



def _save_product(product, form):
   # product.update_images(form.images.data)

    product.update_attributes(form.attributes.data)


    del form.images
    del form.attributes
    form.populate_obj(product)
    product.save()
    return product

def product_del(id):
    product = Product.get_by_id(id)
    Cart.del_product(id)
    if product:
        product.delete()
    return redirect(url_for('dashboard.products'))

def product_manage(id= None):
    image_path = None

    product = Product.get_by_id(id)
    form = ProductForm(obj=product)
    form.current_img.data = product.image_url();

    if form.validate_on_submit():

        product_type = ProductType.get_by_id(product.product_type_id)
        image = form.images.data

        if image:
            filename = upload_file(image)
            ProductImage.del_product_imgs(product.id)
            ProductImage.get_or_create(image=filename, product_id=product.id)
        product.basic_price = form.basic_price.data
        product.title=form.title.data
        product.on_sale = form.on_sale.data
        product.is_active = form.is_active.data
        product.is_featured = form.is_featured.data
        product.in_front_banner = form.in_front_banner.data

        product.save()
        return redirect(url_for("dashboard.product_detail", id=product.id))

    categories = Category.query.all()
    attributes = product.product_type.variant_attributes
    return render_template(
        "product/manage_product.html",
        form=form,categories=categories, attributes=attributes)

def add_product():


    form = ProductForm()
    if form.validate_on_submit():

        product_type = ProductType.get_or_create(
            has_attributes=None, title=form.title.data, is_shipping_required=None,has_variants=None)[0]
        product = Product(product_type_id=product_type.id)
        product.title= product_type.title

        image= form.images.data
        product = _save_product(product, form)
        if image:

            filename= upload_file(image)
            ProductImage.del_product_imgs(product.id)
            ProductImage.get_or_create(image=filename , product_id=product.id)

        if form.variant_attributes.data:
            product_type.has_variants = True
            product_type.save()
            product_type.del_all_variant_attr()
            product_type.update_variant_attr(form.variant_attributes.data)
            product_type.save()
        else:
            product.product_type.has_variants = False
            product_type.del_all_variant_attr()

        product.delete_variants()
        product.generate_variants()
        product.save()
        return redirect(url_for("dashboard.product_detail", id=product.id))

    categories = Category.query.all()
    attributes = ProductAttribute.query.all()
    return render_template(
        "product/add_product.html",
        form=form,
        attributes= attributes,
        categories=categories)




def variant_manage(id=None):
    if id:
        variant = ProductVariant.get_by_id(id)
        form = VariantForm(obj=variant)
    else:
        form = VariantForm()
    if form.validate_on_submit():
        if not id:
            variant = ProductVariant()
        form.populate_obj(variant)
        product_id = request.args.get("product_id")
        if product_id:
            variant.product_id = product_id
        variant.sku = str(variant.product_id) + "-" + str(form.sku_id.data)
        variant.save()
        return redirect(url_for("dashboard.product_detail", id=variant.product_id))
    return render_template("product/variant.html", form=form,variant=variant)
