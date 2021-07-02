# -*- coding: utf-8 -*-
"""Create an application instance."""
import flaskshop

app=flaskshop.create_app()
if __name__ == '__main__':

    app.run(debug=True)


