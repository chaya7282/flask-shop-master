from flaskshop.dashboard.forms import FileImportForm
from flask import request, render_template, redirect, url_for, current_app
import os
from flaskshop.settings import Config
from flaskshop.database import Column, Model, db
from flaskshop.product.models import Product, Category,ProductType,ProductVariant
import pandas as pd
from decimal import Decimal
from sqlalchemy import inspect

def add_to_db(sheet_name, data_type):
    df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"), sheet_name=sheet_name)

    products_to_add = []

    for row in df.to_dict('records'):
        if not pd.isna(row['title']):
            remove = ['None']
            row = dict([(k, v) for k, v in row.items() if v not in remove])
            row = dict([(k, v) for k, v in row.items() if not pd.isna(v)])
            if data_type== "Products":

                products_to_add.append(Product(**row))
            else:
                products_to_add.append(Category(**row))


    db.session.add_all(products_to_add)
    db.session.commit()
    return


#        products_to_add = [Product(**row) for row in df.to_dict('records')]
#       db.session.add_all( products_to_add)


def add_products(sheet_name):
    df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"), sheet_name=sheet_name)

    products_types_to_add = []
    products_to_add = []
    insp = inspect(db.engine)

    columns_table = insp.get_columns( "product_product")  # schema is optional


    for row in df.to_dict('records'):
        remove = ['None']
        row = dict([(k, v) for k, v in row.items() if v not in remove and not pd.isna(v)])
        if 'title' in row:

            products_types_to_add.append(ProductType(title=row['title'], is_shipping_required=False,has_variants=False))
            if 'basic_price' in row:
                row['basic_price']= float(str(row['basic_price']).replace(',',''))
                print( row['basic_price'])
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
    db.session.commit()

    product_variant_add=[]
    productTypes_query= ProductType.query.all()
    products_query= Product.query.all()
    products_to_add = []
    for idx in range(len(products_query)):
         products_query[idx].product_type_id= productTypes_query[idx].id
    db.session.commit()

    products_query = Product.query.all()
    product_variants=[]
    for idx in range(len( products_query)):
        product_variants.append( ProductVariant(sku=str(products_query[idx].id) + "-1337", product_id=products_query[idx].id, title= products_query[idx].title))
    db.session.add_all(product_variants)
    db.session.commit()


def file_data_import():
    image_path = None

    form =FileImportForm()

    if form.validate_on_submit():
        xls_file= form.xls_file.data
        xls_file.save(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"))

        add_products("Products")
        add_to_db("Categories", "Categories")
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



def exportexcel():
    if request.method == 'POST':
        filename = os.path.join(Config.UPLOAD_FOLDER, "autos.xlsx")
        writer = pd.ExcelWriter(filename)


        data = Product.query.all()
        data_list = [to_dict(item) for item in data]
        remove = ['created_at', 'updated_at','id']
        for idx in range(len(data_list)):
            data_list[idx] = dict([(k, v) for k, v in data_list[idx].items() if k not in remove])

        df_product = pd.DataFrame(data_list)
        df_product= df_product.fillna('None')
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
    else:
        return render_template("ImportDataFromFile/export_toxls.html")

    return redirect(url_for('dashboard.index') )