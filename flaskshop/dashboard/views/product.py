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
from werkzeug import secure_filename
from PIL import Image

from PIL import Image
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


def attributes_manage(id=None):
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
        attr.update_types(form.types.data)
        attr.update_values(form.values.data)
        attr.save()
        return redirect(url_for("dashboard.attributes"))

    return render_template(
        "product/attribute.html", form=form,
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
    pagination = Category.query.paginate(page, 10)
    props = {
        "id": "ID",
        "title": "Title",
        "parent": "Parent",
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


def categories_manage(id=None):
    if id:
        category = Category.get_by_id(id)
        form = CategoryForm(obj=category)
    else:
        form = CategoryForm()
    if form.validate_on_submit():
        if not id:
            category = Category()
        category.title = form.title.data
        category.parent_id = form.parent_id.data
        image = form.bgimg_file.data
        if image:
            filename=load_image(image)
            category.background_img=filename

        else:
            category.background_img = None
        category.save()
        return redirect(url_for("dashboard.categories"))
    parents = Category.first_level_items()
    return render_template("product/category.html", form=form, parents=parents)


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

    on_sale = request.args.get("sale", type=int)
    if on_sale is not None:
        query = query.filter_by(on_sale=on_sale)
    category = request.args.get("category", type=int)
    if category:
        query = query.filter_by(category_id=category)
    title = request.args.get("title", type=str)
    if title:
        query = query.filter(Product.title.like(f"%{title}%"))
    created_at = request.args.get("created_at", type=str)
    if created_at:
        start_date, end_date = created_at.split("-")
        start_date = datetime.strptime(start_date.strip(), "%m/%d/%Y")
        end_date = datetime.strptime(end_date.strip(), "%m/%d/%Y")
        query = query.filter(Product.created_at.between(start_date, end_date))

    pagination = query.paginate(page, 10)
    props = {
        "id": "ID",
        "title": "כותרת",
        "on_sale_human": "בסייל",
        "sold_count": "כמות שנמכרה",
        "price_human": "מחיר",
        "category": "קטגוריה",
    }
    context = {
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "categories": Category.query.all(),
    }
    return render_template("product/list.html", **context)


def product_detail(id):
    product = Product.get_by_id(id)

    return render_template("product/detail.html", product=product)



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
    if product:
        product.delete()
    return redirect(url_for('dashboard.products'))

def product_edit(id):
    product = Product.get_by_id(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        f = request.files['imgdata']
        if f:
            image_name= load_image(f.filename)
            new_img= ProductImage.get_or_create(image=image_name, product_id=product.id)
            Product.update_images([new_img[0].id],product.id)

        _save_product(product, form)
        return redirect(url_for("dashboard.product_detail", id=product.id))
    categories = Category.query.all()
    context = {"form": form, "categories": categories, "product": product }
    return render_template("product/product_edit.html", **context)




def product_create_step1(id=None):
    if id:
        product_type = ProductType.get_by_id(id)
        form = ProductTypeForm(obj=product_type)
    else:
        form = ProductTypeForm()
    if form.validate_on_submit():
        if not id:
            request.form.getlist('usergroups')
            isChecked = request.form.getlist("HasAttributes")
            has_attributes = False
            if isChecked:
                has_attributes= True
            isChecked = request.form.getlist("HasVariants")
            has_variants = False
            if isChecked:
                has_variants = True


            product_type = ProductType.get_or_create(
                has_attributes=has_attributes, title=form.title.data, is_shipping_required=form.is_shipping_required.data, has_variants = has_variants)[0]

            if product_type.has_attributes:
                for attr in form.product_attributes.data:
                    ProductTypeAttributes.get_or_create(
                        product_type_id=product_type.id, product_attribute_id=int(attr)
                    )


            product_type.save()
            return  redirect(url_for(
                    "dashboard.product_create_step2",
                    product_type_id=product_type.id
                ))
    attributes = ProductAttribute.query.all()
    return render_template(
        "product/product_create_step1.html", form=form, attributes=attributes
    )
def load_image(image):
    if image:
        baseheight= 400
        image.save(os.path.join(Config.UPLOAD_FOLDER, "tmp_file.jpg"))
        im = Image.open(os.path.join(Config.UPLOAD_FOLDER, "tmp_file.jpg"))
        wpercent = (baseheight / float(im.size[1]))
        wsize = int((float(im.size[0]) * float(wpercent)))
        im= im.resize((wsize,baseheight), Image.ANTIALIAS)
        preffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join(["a", preffix, image.filename])  # e.g. 'mylogfile_120508_171442'
        im.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        return filename

def product_create_step2():
    form = ProductForm()

    categories = Category.query.all()

    if form.validate_on_submit():
        product_type = ProductType.get_or_create(
            has_attributes=None, title=form.title.data, is_shipping_required=None,has_variants=None)[0]

        product = Product(product_type_id=product_type.id)
        product.title= product_type.title

        image= form.images.data
        product = _save_product(product, form)
        if image:
            filename= load_image(image)
            ProductImage.get_or_create(image=filename , product_id=product.id)
        if product_type.has_variants:
            for attr in form.variant_attributes.data:
                ProductTypeVariantAttributes.get_or_create(product_type_id=product_type.id,
                                                           product_attribute_id=int(attr))

        product.generate_variants()
        return redirect(url_for("dashboard.product_detail", id=product.id))

    attributes = ProductAttribute.query.all()
    return render_template(
        "product/add_product.html",
        form=form,
        categories=categories,

   )


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
    return render_template("product/variant.html", form=form)
