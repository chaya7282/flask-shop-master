from flask import Flask
from flaskshop.configuration import create_app

app = Flask(__name__.split(".")[0])
create_app(app)