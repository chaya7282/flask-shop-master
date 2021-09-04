from flask_script import Manager
from flaskshop import random_data
import flaskshop

app= flaskshop.create_app()
manager = Manager(app)
import flaskshop.commands as commands

@manager.command
def createdb():
    commands.createdb()
@manager.command
def seed(type):
    commands.seed(type)

@manager.command
def destroydb():
    commands.destroydb()
@manager.command
def create_admin():
    commands.create_admin_cmd()
@manager.command
def create_dashboard_menus():
    commands.create_dashboard_menus_cmd()



def seed(type):
    commands.seed(type)



def inits():
    commands.destroydb()
    commands.createdb()
    commands.create_admin()
    commands.create_dashboard_menus()
    commands.seed("product")


if __name__ == "__main__":

    manager.run()

    manager.add_command('createdb', createdb())
    manager.add_command('destroydb', destroydb())
    manager.add_command('create_admin', create_admin())
    manager.add_command('create_dashboard_menus', create_dashboard_menus())
    manager.add_command('seed', seed())
    manager.add_command('inits', inits())