# -*- coding: utf-8 -*-
"""Create an application instance."""
import flaskshop
from flask_mail import Mail

app=flaskshop.create_app()
mail = Mail(app)
if __name__ == '__main__':

    app.run(debug=True)


