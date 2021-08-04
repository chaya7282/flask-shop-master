import mysql.connector as mysql
from flask_sqlalchemy import SQLAlchemy
## connecting to the database using 'connect()' method
## it takes 3 required parameters 'host', 'user', 'passwd'
db =SQLAlchemy()

print(db)