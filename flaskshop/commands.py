# -*- coding: utf-8 -*-
"""Click commands."""
from subprocess import call
import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.exceptions import MethodNotAllowed, NotFound
from pathlib import Path
from itertools import chain
from flaskshop.random_data import DEFAULT_SCHEMA2
from pathlib import Path
import pickle
import json
import codecs
from flaskshop.random_data import (
    create_users,
    create_menus,
    create_shipping_methods,
    create_products_by_schema,
    create_page,
    create_collections_by_schema,
    create_categories_by_schema,
    create_admin,
    create_orders,
    create_product_sales,
    create_vouchers,
    create_dashboard_menus,
    create_roles,
    create_bussiness,
)
from flaskshop.extensions import db
from flaskshop.corelib.db import rdb
from flaskshop.public.search import Item
from flaskshop.product.models import Product

HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parent
TEST_PATH = "tests"


@click.command()
def test():
    """Run the tests."""
    print(call(f"pytest {TEST_PATH}", shell=True))


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=False,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
def lint(fix_imports):
    """Lint and check code style with flake8 and isort."""
    skip = ["node_modules", "requirements"]
    root_files = Path(PROJECT_ROOT).glob("*.py")
    root_directories = (
        file for file in Path(PROJECT_ROOT).iterdir() if not file.name.startswith(".")
    )

    files_and_directories = [
        arg.name for arg in chain(root_files, root_directories) if arg.name not in skip
    ]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo(f"{description}: {' '.join(command_line)}")
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if fix_imports:
        execute_tool("Fixing import order", "isort", "-rc")
    execute_tool("Checking code style", "flake8")


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for file in chain(
        Path(PROJECT_ROOT).glob("**/*.pyc"), Path(PROJECT_ROOT).glob("**/*.pyo")
    ):
        click.echo(f"Removing {file}")
        file.unlink()


@click.command()
@click.option("--url", default=None, help="Url to test (ex. /static/image.png)")
@click.option(
    "--order", default="rule", help="Property on Rule to order by (default: rule)"
)
@with_appcontext
def urls(url, order):
    """Display all of the url matching routes for the project.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_headers = ("Rule", "Endpoint", "Arguments")

    if url:
        try:
            rule, arguments = current_app.url_map.bind("localhost").match(
                url, return_rule=True
            )
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append((f"<{e}>", None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(), key=lambda rule: getattr(rule, order)
        )
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ""
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += "{:" + str(max_rule_length) + "}"
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        # max_endpoint_length = max(rows, key=len)
        max_endpoint_length = max_endpoint_length if max_endpoint_length > 8 else 8
        str_template += "  {:" + str(max_endpoint_length) + "}"
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = max_arguments_length if max_arguments_length > 9 else 9
        str_template += "  {:" + str(max_arguments_length) + "}"
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo("-" * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))





def createdb():
    """ create database tables
    """
    db.create_all()

def destroydb():
    """ destory database tables
    """
    db.drop_all()

def create_admin_cmd():
    create_generator = chain(
        create_roles(),
        create_admin(),
    )
    for msg in create_generator:
        click.echo(msg)

def  create_dashboard_menus_cmd():

    create_generator = chain(

        create_dashboard_menus(),
    )
    for msg in create_generator:
        click.echo(msg)

def create_products_by_schema_cmd():
    place_holder = Path("placeholders")
    create_generator = chain(

        create_products_by_schema(
            placeholder_dir=place_holder, how_many=1, create_images=False
        )
    )
    for msg in create_generator:
        click.echo(msg)

def save_store_to_cmd():

    dictionary_data = {"a": 1, "b": 2}
    with open("codebeautify.json", "w") as outfile:
        json.dump(DEFAULT_SCHEMA2, outfile)


def load_store_from_xls_cmd(xls):
     db.drop_all()
     db.create_all()
     with open('data.json') as json_file:
         data = json.load(json_file)
     print(data["a"])





def create_shipping_methods_cmd():
    create_generator = chain(

        create_shipping_methods(),
    )
    for msg in create_generator:
        click.echo(msg)





def seed(type):
    """ Generate random data for test.
    """
    if type == "limited":
        db.drop_all()
        db.create_all()

        place_holder = Path("placeholders")
        create_categories_by_schema(placeholder_dir=place_holder),
        create_products_by_schema(
            placeholder_dir=place_holder, how_many=5, create_images=False
        )

        create_generator = chain(
            create_roles(),
            create_admin(),

            create_shipping_methods(),

          create_dashboard_menus(),
        )
        for msg in create_generator:
            click.echo(msg)

    elif type == "default":
        place_holder = Path("placeholders")
        create_products_by_schema(
            placeholder_dir=place_holder, how_many=1, create_images=True
        )
        create_generator = chain(
            create_collections_by_schema(place_holder),
            create_users(),
            create_roles(),
            create_admin(),
            create_page(),
            create_menus(),
            create_shipping_methods(),
            create_dashboard_menus(),
            create_orders(),
            create_product_sales(),
            create_vouchers(),
        )
        for msg in create_generator:
            click.echo(msg)

    elif type == "product":

        place_holder = Path("placeholders"),
        create_products_by_schema(
            placeholder_dir=place_holder, how_many=5, create_images=False
        )

        create_generator = chain(


            create_roles(),
            create_admin(),


            create_shipping_methods(),
            create_dashboard_menus(),

        )

        for msg in create_generator:
            click.echo(msg)
    elif type == "product_2":
        db.drop_all()
        db.create_all()

        place_holder = Path("placeholders"),

        create_generator = chain(

            create_roles(),
            create_admin(),
            create_bussiness(),
            create_shipping_methods(),
            create_dashboard_menus(),

        )

        for msg in create_generator:
            click.echo(msg)
    else:
        create_dict = {
            "user": create_users,
            "menu": create_menus,
            "ship": create_shipping_methods,
            "order": create_orders,
            "sale": create_product_sales,
            "voucher": create_vouchers,
            "dashboard": create_dashboard_menus,
            "role": create_roles,
        }
        fn = create_dict[type]
        for msg in fn():
            click.echo(msg)


@click.command()
@with_appcontext
def flushrdb():
    """ Clear all redis keys, include cache and propitems.
    """
    rdb.flushdb()


@click.command()
@with_appcontext
def reindex():
    """ clear elastic-search items.
    """
    Item._index.delete(ignore=404)
    Item.init()
    products = Product.query.all()
    Item.bulk_update(products, op_type="create")
