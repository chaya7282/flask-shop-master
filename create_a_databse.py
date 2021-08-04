import mysql.connector as mysql
from flask_sqlalchemy import SQLAlchemy
## connecting to the database using 'connect()' method
## it takes 3 required parameters 'host', 'user', 'passwd'
db =SQLAlchemy(pool_pre_ping=True, pool_recycle=3600)

print(db)