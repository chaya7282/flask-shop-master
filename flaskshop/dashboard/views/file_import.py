from flaskshop.dashboard.forms import FileImportForm
from flask import request, render_template, redirect, url_for, current_app
def file_data_import():
    image_path = None

    form =FileImportForm()

    if form.validate_on_submit():
        i=7;

    return render_template("ImportDataFromFile/importFromFile.html", form=form)