from flask import Flask

from flaskshop import commands
from flaskshop.settings import Config
from flaskshop import configuration
from flaskshop.plugin.models import PluginRegistry
from flaskshop.settings import Config
from flaskshop.plugin import spec, manager
import paypalrestsdk
import pandas as pd
import os
def create_app():
    app = Flask(__name__)

    app.config['UPLOAD_FOLDER']=settings.Config.UPLOAD_FOLDER
    app.config["SESSION_TYPE"] = "filesystem"



    app.config.from_object(Config)
    app.pluggy = manager.FlaskshopPluginManager("flaskshop")
    configuration.register_extensions(app)
    configuration.load_plugins(app)
    configuration.register_blueprints(app)
    configuration.register_errorhandlers(app)
    configuration.register_shellcontext(app)
    configuration.register_commands(app)
    configuration.jinja_global_varibles(app)
    configuration.log_slow_queries(app)

    app.wsgi_app = configuration.DispatcherMiddleware(app.wsgi_app, {"/dashboard_api": configuration.dashboard_api})
    return app

#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#app.config['CACHE_TYPE'] = None

