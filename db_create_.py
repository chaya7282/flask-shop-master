import flaskshop.commands
from flaskshop.extensions import db

db.create_all()
flaskshop.commands.seed()
