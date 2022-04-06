# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask_mail import Mail
import os
import flaskshop

app=flaskshop.create_app()
mail = Mail(app)

if __name__ == '__main__':

    app.run(debug=False)


