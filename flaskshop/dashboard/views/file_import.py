from flaskshop.dashboard.forms import FileImportForm, FileExportForm
from flask import request, render_template, redirect, url_for, current_app
import os
from flaskshop.settings import Config
from flaskshop.database import Column, Model, db
from flaskshop.product.models import Product, Category,ProductType,ProductVariant, ProductImage, AttributeChoiceValue,ProductAttribute,ProductTypeVariantAttributes
from flask import send_file, send_from_directory, safe_join, abort
import pandas as pd

from decimal import Decimal
from sqlalchemy import inspect
from flask import flash
def add_categories(sheet_name):
    df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"), sheet_name=sheet_name)
    Category.query.delete()
    products_to_add = []

    for row in df.to_dict('records'):
        if 'title' in row:
            remove = ['None']
            row = dict([(k, v) for k, v in row.items() if v not in remove])
            row = dict([(k, v) for k, v in row.items() if not pd.isna(v)])
            products_to_add.append(Category(**row))


    db.session.add_all(products_to_add)
    db.session.commit()
    return


#        products_to_add = [Product(**row) for row in df.to_dict('records')]
#       db.session.add_all( products_to_add)

def clean_DataFrame(df):
    df2 = df.loc[df["Fee"] >= 24000]
def add_attributes(sheet_name):
    ProductAttribute.query.delete()

    df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"), sheet_name=sheet_name)
    if not df.empty:
        for row in df.to_dict('records'):
            if 'title' in row:
                attr = ProductAttribute()
                attr.title = row['title']
                attr.save()
def add_attributes_choice(sheet_name):
    AttributeChoiceValue.query.delete()
    df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"), sheet_name=sheet_name)
    if not df.empty:
        for row in df.to_dict('records'):
            if 'title' in row:
                attr_choice = AttributeChoiceValue()
                attr_choice.title = row['title']
                attr_choice.image=row['Image']
                attr=ProductAttribute.query.filter_by(title=row["attribute"]).first()
                attr_choice.attribute_id=attr.id
                attr_choice.save()
def add_product_attributes(sheet_name):
    df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"), sheet_name=sheet_name)
    ProductTypeVariantAttributes.query.delete()
    if not df.empty:
        for row in df.to_dict('records'):
            if 'product' in row:
                product= Product.query.filter_by(title=row["product"]).first()
                product_type = ProductType.get_by_id(product.product_type_id)
                product_type.has_variants = True
                product_type.save()
                attr=ProductAttribute.query.filter_by(title=row["attribute"]).first()
                product_type.update_variant_attr([attr.id])
                product_type.save()
                product.delete_variants()
                product.generate_variants()
                product.save()

def add_products(sheet_name,type):
    Product.query.delete()
    ProductImage.query.delete()
    df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"), sheet_name=sheet_name)
    if not df.empty:
        if type == "cash_register":
            df['Unnamed: 0']= df['Unnamed: 6']
            df['Unnamed: 1']= df['Unnamed: 9'].fillna("") + df['Unnamed: 8'].fillna("")
            df = df[pd.to_numeric(df['Unnamed: 0'], errors='coerce').notnull()]
            df = df[(df['Unnamed: 1'] != "")]
            df= df[['Unnamed: 1', 'Unnamed: 0']]
            df=df.rename(columns={'Unnamed: 1': "title",'Unnamed: 0': "basic_price"})
            df['category_name'] = df['title'].str[:1]
            options =["א","ב","ג","ד","ה","ו","ז","ח","ט","י","כ","ל","מ","נ","ס","ע","פ","צ","ק","ר","ש","ת"]
            df = df[df['category_name'].isin(options)]
        df= df.drop_duplicates(subset="title", keep="last")
    else:
        return

    products_types_to_add = []
    products_to_add = []


    for row in df.to_dict('records'):
        remove = ['None']
        row = dict([(k, v) for k, v in row.items() if v not in remove and not pd.isna(v)])
        if 'title' in row:

            products_types_to_add.append(ProductType(title=row['title'], is_shipping_required=False,has_variants=False))

            product = Product(**row)

            category=None
            if 'category_name' in row:
                category_db= Category.query.filter_by(title= row['category_name']).first()
                if not category_db:
                    category_db=Category()
                    category_db.title= row['category_name']
                    db.session.add(category_db)
                    db.session.commit()
                product.category_id= category_db.id

            products_to_add.append(product)
    db.session.add_all(products_types_to_add)
    db.session.add_all(products_to_add)
    items=  Product.query.all()


    db.session.commit()

    product_variant_add=[]
    productTypes_query= ProductType.query.all()
    products_query= Product.query.all()
    products_to_add = []
    for idx in range(len(products_query)):
         product_type= ProductType.query.filter_by(title=products_query[idx].title).first()
         product=Product.query.filter_by(title=products_query[idx].title).first()

         product.product_type_id=product_type.id
    db.session.commit()

    products_query = Product.query.all()
    product_variants=[]
    product_images=[]
    for idx in range(len( products_query)):
        product_variants.append( ProductVariant(sku=str(products_query[idx].id) + "-1337", product_id=products_query[idx].id, title= products_query[idx].title))
        product_images.append(ProductImage(image=products_query[idx].background_img, product_id=products_query[idx].id))

    db.session.add_all(product_variants)
    db.session.add_all(product_images)
    db.session.commit()

def file_data_import():
    image_path = None

    form =FileImportForm()

    if form.validate_on_submit():
        xls_file= form.xls_file.data
        xls_file.save(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"))
        try:
            add_categories("Categories", "Categories")
            add_products("Products","cash_register")
            add_attributes("attributes")
        except:
            flash('problem in operation try again')
            return redirect(url_for('dashboard.index'))
        db.session.commit()

        return redirect(url_for('dashboard.index'))
    return render_template("ImportDataFromFile/importFromFile.html", form=form)


def to_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict


def get_report(path):
    filename= os.path.join(path, "autos.xlsx")




def exportexcel():

    form =  FileExportForm()

    if form.validate_on_submit():

        filename = os.path.join(Config.CLIENT_REPORTS, "autos.xlsx")
        try:
            writer = pd.ExcelWriter(filename)
        except:
            flash('problem with directory')
            return redirect(url_for('dashboard.index'))
        data = Product.query.all()
        data_list = [to_dict(item) for item in data]
        remove = ['created_at', 'updated_at','id','attributes','category_id','sold_count','review_count','product_type_id','rating']
        for idx in range(len(data_list)):
            data_list[idx] = dict([(k, v) for k, v in data_list[idx].items() if k not in remove])

        df_product = pd.DataFrame(data_list)
        df_product= df_product.fillna('None')
        df_product= df_product.replace({'':'None'})


        df_product.to_excel(writer, sheet_name='Products',index=False)

        data = Category.query.all()
        data_list = [to_dict(item) for item in data]
        remove = ['created_at', 'updated_at', 'id']
        for idx in range(len(data_list)):
            data_list[idx] = dict([(k, v) for k, v in data_list[idx].items() if k not in remove])

        df_product = pd.DataFrame(data_list)
        df_product.where(pd.notnull(df_product), None)
        df_product.to_excel(writer, sheet_name='Categories',index=False)

        writer.save()

        return send_file( os.path.join(Config.CLIENT_REPORTS, "autos.xlsx"))


    return render_template("ImportDataFromFile/export_toxls.html", form=form)

def Import_Products_db_xls():
    form = FileImportForm()

    if form.validate_on_submit():
        xls_file = form.xls_file.data
        xls_file.save(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"))

        add_categories("Categories")
        add_products("Products","db_file")
        add_attributes("attributes")
        add_attributes_choice("attribute_choice")
        add_product_attributes("products_attributes")
        db.session.commit()

        return redirect(url_for('dashboard.index'))
    return render_template("ImportDataFromFile/Import_Products_db_xls.html", form=form)


def Import_Cash_Registe_xls():
    form = FileImportForm()

    if form.validate_on_submit():
        xls_file = form.xls_file.data
        xls_file.save(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"))
        try:
            add_products( "Sheet1","cash_register")
        except:
            flash('problem in operation try again')
            return redirect(url_for('dashboard.index'))
        db.session.commit()

        return redirect(url_for('dashboard.index'))
    return render_template("ImportDataFromFile/Import_Cash_Registe_xls.html", form=form)

def Import_Categories_db_xls():
    form = FileImportForm()

    if form.validate_on_submit():
        xls_file = form.xls_file.data
        xls_file.save(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"))
        try:
            add_categories("Categories")
        except:
            flash('problem in operation try again')
            return redirect(url_for('dashboard.index'))
        db.session.commit()

        return redirect(url_for('dashboard.index'))
    return render_template("ImportDataFromFile/Import_Categories_db_xls.html", form=form)
