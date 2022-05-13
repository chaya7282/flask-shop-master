from flaskshop.dashboard.forms import  BussinessForm
from flaskshop.account.models import Business
from flaskshop.Media.media import load_image, upload_file, get_image_url
from flask import request, render_template,redirect,url_for

def manage_bussiness():
    bussines = Business.query.first()

    form = BussinessForm(obj=bussines)

    if form.validate_on_submit():
        if not bussines:
            bussines=  Business()

        form.populate_obj(bussines)

        image= form.image.data

        if image:

            filename= upload_file(image)
            bussines.image = filename
        bussines.save()
        return redirect(url_for('dashboard.index'))

    return render_template("bussiness/bussiness.html",form=form)


