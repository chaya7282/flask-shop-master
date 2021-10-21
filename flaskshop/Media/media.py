from PIL import Image
from flaskshop.settings import Config
import os
import datetime
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
        im.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        return filename