# -*- coding: utf-8 -*-
"""Click commands."""
from flask_script import Manager
from flaskshop import random_data
import flaskshop
import flaskshop.commands as commands
app= flaskshop.create_app()
manager = Manager(app)

if __name__ == "__main__":

    manager.run()
    manager.se