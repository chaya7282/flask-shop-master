from flask import Flask
from flaskshop.configuration import create_app

app = Flask(__name__.split(".")[0])
create_app(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['CACHE_TYPE'] = None
