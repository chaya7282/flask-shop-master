# -*- coding: utf-8 -*-
"""Create an application instance."""
from flaskshop.app import create_app
from flaskshop.app import commands

app = create_app()
app.run()

