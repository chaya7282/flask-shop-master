from PIL import Image
from flaskshop.settings import Config
from flask import session, current_app
import os
import io
import datetime
from flaskshop.resources.resources import get_bucket, get_buckets_list,get_presigned_url
def load_image(image,placeholder):
    if image:
        baseheight= 400
        image.save(os.path.join(Config.UPLOAD_FOLDER, "tmp_file.jpg"))
        im = Image.open(os.path.join(Config.UPLOAD_FOLDER, "tmp_file.jpg"))
        wpercent = (baseheight / float(im.size[1]))
        wsize = int((float(im.size[0]) * float(wpercent)))
        im= im.resize((wsize,baseheight), Image.ANTIALIAS)
        preffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join(["a", preffix, image.filename])  # e.g. 'mylogfile_120508_171442'
        filename= placeholder+ "//"+filename
        return filename

def load_image_AWS(image):
    if image:

        baseheight = 400
        image.save(os.path.join(Config.UPLOAD_FOLDER, "tmp_file.jpg"))
        loaded_image = Image.open(os.path.join(Config.UPLOAD_FOLDER, "tmp_file.jpg"))
        saved_quantized_image = io.BytesIO()
        loaded_image.save(saved_quantized_image, 'PNG')

        preffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join(["a", preffix, image.filename])  # e.g. 'mylogfile_120508_171442'

        return filename, saved_quantized_image

def upload_file(file):

    key,file= load_image_AWS(file)
    my_bucket = get_bucket()
    file.seek(0)

    my_bucket.Object(key).put(Body=file)


    return key


def download_file(key):
    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()
    return file_obj;

def get_image_url(key):
    url= get_presigned_url(key)
    return url