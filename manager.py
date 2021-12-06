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
@manager.command
def create_shipping_methods():
    commands.create_shipping_methods_cmd()

@manager.command
def create_shipping_methods():
    commands.create_shipping_methods_cmd()


def load_products_from_xls(type):
    commands.seed(type)

@manager.command
def load_store_from_xls() :
    commands.load_store_from_xls_cmd("C://Users//User//PycharmProjects//flask-shop//flask-shop-master//codebeautify.json")

@manager.command
def save_store():
    commands.save_store_to_cmd()

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
    manager.add_command('create_shipping_methods', create_dashboard_menus())
    manager.add_command('load_store_from_xls', load_store_from_xls())

    manager.add_command('save_store', save_store())


    manager.add_command('seed', seed())
    manager.add_command('inits', inits())