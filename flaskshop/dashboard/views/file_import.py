from flaskshop.dashboard.forms import FileImportForm
from flask import request, render_template, redirect, url_for, current_app
import os
from flaskshop.settings import Config
from flaskshop.database import Column, Model, db
from flaskshop.product.models import Product
import pandas as pd
def file_data_import():
    image_path = None

    form =FileImportForm()

    if form.validate_on_submit():
        xls_file= form.xls_file.data
        xls_file.save(os.path.join(Config.UPLOAD_FOLDER, "xls_source.xls"))

        df = pd.read_excel(os.path.join(Config.UPLOAD_FOLDER,"xls_source.xls"),sheet_name='Sheet4' )
        products_to_add =[]
        for row in df.to_dict('records'):
            if not pd.isna(row['title']):
                products_to_add.append(Product(**row))
#        products_to_add = [Product(**row) for row in df.to_dict('records')]
        db.session.add_all( products_to_add)
        db.session.commit()
    return render_template("ImportDataFromFile/importFromFile.html", form=form)