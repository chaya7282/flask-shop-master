# -*- coding: utf-8 -*-
"""Create an application instance."""
from flaskshop.app import create_app
from flaskshop.app import commands


if __name__ == '__main__':
    app = create_app()
    app.run()

