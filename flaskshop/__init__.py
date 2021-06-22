from flask import Flask
from flaskshop.app import create_app

app = Flask(__name__)
create_app(app)