from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required
from pluggy import HookimplMarker
from sqlalchemy import func
from flaskshop.extensions import db
from flaskshop.dashboard.models import DashboardMenu
from flaskshop.order.models import Order, OrderLine, OrderEvent
from flaskshop.product.models import Product
from flaskshop.account.models import User
from flaskshop.account.utils import permission_required
from flaskshop.settings import Config
from flaskshop.constant import Permission, OrderStatusKinds, OrderEvents
from.bussiness import manage_bussiness
from .user import users, user, user_edit, address_edit, user_del
from .site import (
    shipping_methods,
    shipping_methods_manage,
    shipping_methods_del,
    site_menus,
    site_menus_manage,
    dashboard_menus,
    dashboard_menus_manage,
    site_pages,
    site_pages_manage,
    site_setting,
    plugin_list,
    plugin_enable,
    plugin_disable,
    config_index,
)
from .product import (
    attributes,
    attributes_manage,
    attributes_del,
    collections,
    collections_manage,
    categories,
    categories_manage,
    product_types,
    product_types_manage,
    products,
    product_detail,
    product_manage,
    add_product,
    categories_del,
    categories_detail,
    variant_manage,
    product_del,
)
from .order import orders, order_detail, send_order, draft_order, order_edit,order_del
from .discount import vouchers, vouchers_manage, sales, sales_manage
from .file_import import file_data_import,exportexcel, Import_Categories_db_xls,Import_Products_db_xls,Import_Cash_Registe_xls
impl = HookimplMarker("flaskshop")


def index():
    def get_today_num(model):
        target = db.cast(datetime.now(), db.DATE)
        which = db.cast(model.created_at, db.DATE)
        return model.query.filter(which == target).count()

    def get_order_status(status):
        return {
            "count": Order.query.filter_by(status=status).count(),
            "kind": status,
        }

    onsale_products_count = Product.query.filter_by(on_sale=True).count()

    hot_product_ids = (
        db.session.query(OrderLine.product_id, func.count(OrderLine.product_id))
        .group_by(OrderLine.product_id)
        .order_by(func.count(OrderLine.product_id).desc())
        .all()
    )
    top5_products = []


    activity = OrderEvent.query.order_by(OrderEvent.id.desc()).limit(10)

    context = {
        "orders_total": Order.query.count(),
        "orders_today": get_today_num(Order),
        "users_total": User.query.count(),
        "users_today": get_today_num(User),
        "order_unfulfill": get_order_status(OrderStatusKinds.unfulfilled.value),
        "order_fulfill": get_order_status(OrderStatusKinds.fulfilled.value),
        "onsale_products_count": onsale_products_count,
        "top_products": top5_products,
        "activity": activity,
        "order_events": OrderEvents,
    }
    return render_template("index.html", **context)

def Catalog():
    return render_template("Catalog.html")
@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint(
        "dashboard", __name__, template_folder=Config.DASHBOARD_TEMPLATE_FOLDER
    )

    @bp.context_processor
    def inject_param():
        menus = DashboardMenu.first_level_items()
        return {"menus": menus}

    @bp.before_request
    @permission_required(Permission.EDITOR)
    @login_required
    def before_request():
        """The whole blueprint need to login first"""
        pass

    bp.add_url_rule("/", view_func=index)
    bp.add_url_rule("/Catalog", view_func=Catalog)
    bp.add_url_rule("/site_menus", view_func=site_menus)
    bp.add_url_rule(
        "/site_menus/create", view_func=site_menus_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/site_menus/<id>/edit", view_func=site_menus_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule("/dashboard_menus", view_func=dashboard_menus)
    bp.add_url_rule(
        "/dashboard_menus/create",
        view_func=dashboard_menus_manage,
        methods=["GET", "POST"],
    )
    bp.add_url_rule(
        "/dashboard_menus/<id>/edit",
        view_func=dashboard_menus_manage,
        methods=["GET", "POST"],
    )
    bp.add_url_rule("/site_pages", view_func=site_pages)
    bp.add_url_rule(
        "/site_pages/create", view_func=site_pages_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/site_pages/<id>/edit", view_func=site_pages_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule("/site_setting", view_func=site_setting, methods=["GET", "POST"])
    bp.add_url_rule("/plugin", view_func=plugin_list)
    bp.add_url_rule("/plugin/<id>/enable", view_func=plugin_enable, methods=["POST"])
    bp.add_url_rule("/plugin/<id>/disable", view_func=plugin_disable, methods=["POST"])
    bp.add_url_rule("/config", view_func=config_index)
    bp.add_url_rule("/users", view_func=users)
    bp.add_url_rule("/users/<user_id>", view_func=user)
    bp.add_url_rule(
        "/users/<user_id>/edit", view_func=user_edit, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/users/address/<id>/edit", view_func=address_edit, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/users/<user_id>/user_del", view_func=user_del, methods=["GET", "POST"]
    )


    bp.add_url_rule("/attributes", view_func=attributes)

    bp.add_url_rule(
        "/attributes/<id>/del", view_func=attributes_del, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/attributes/create", view_func=attributes_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/attributes/<id>/edit", view_func=attributes_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule("/collections", view_func=collections)
    bp.add_url_rule(
        "/collections/create", view_func=collections_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/collections/<id>/edit", view_func=collections_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule("/categories", view_func=categories,methods=["GET", "POST"])
    bp.add_url_rule(
        "/categories/create", view_func=categories_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/categories/<id>/edit", view_func=categories_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule("/product_types", view_func=product_types)
    bp.add_url_rule(
        "/product_types/create", view_func=product_types_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/product_types/<id>/edit",
        view_func= product_types_manage,
        methods=["GET", "POST"],
    )
    bp.add_url_rule("/shipping_methods", view_func=shipping_methods)
    bp.add_url_rule("/ shipping_methods_del/<id>", view_func= shipping_methods_del)


    bp.add_url_rule(
        "/shipping_methods/create",
        view_func=shipping_methods_manage,
        methods=["GET", "POST"],
    )
    bp.add_url_rule(
        "/shipping_methods/<id>/edit",
        view_func=shipping_methods_manage,
        methods=["GET", "POST"],
    )
    bp.add_url_rule("/products", view_func=products, methods=["GET", "POST"])
    bp.add_url_rule("/products/<id>", view_func=product_detail)
    bp.add_url_rule("/categories/<id>", view_func=categories_detail )
    bp.add_url_rule("/product_del/<id>", view_func=product_del)
    bp.add_url_rule("/category_del/<id>", view_func= categories_del)

    bp.add_url_rule(
        "/Import_Cash_Registe_xls", view_func=Import_Cash_Registe_xls, methods=["GET", "POST"],
    )
    bp.add_url_rule(
        "/Import_Categories_db_xls", view_func=Import_Categories_db_xls, methods=["GET", "POST"],
    )
    bp.add_url_rule(
        "/Import_Products_db_xls", view_func=Import_Products_db_xls, methods=["GET", "POST"],
    )

    bp.add_url_rule(
        "/exportexcel", view_func=exportexcel, methods=["GET", "POST"],
    )

    bp.add_url_rule(
        "/products/create/step2",view_func=product_manage, methods=["GET", "POST"],
    )
    bp.add_url_rule(
        "/bussiness/manage_bussiness", view_func=manage_bussiness, methods=["GET", "POST"],
    )
    bp.add_url_rule(
        "/products/<id>/edit", view_func= product_manage, methods=["GET", "POST"]
    )

    bp.add_url_rule(
        "/products/add_product", view_func=add_product, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/products/variant/create", view_func=variant_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/products/variant/<id>/edit", view_func=variant_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule("/orders", view_func=orders,methods=["GET", "POST"] )

    bp.add_url_rule("/orders/<id>/detail", view_func=order_detail)
    bp.add_url_rule("/orders/<id>/edit", view_func=order_edit, methods=["GET", "POST"] )
    bp.add_url_rule("/orders/<id>/send", view_func=send_order)
    bp.add_url_rule("/orders/<id>/draft", view_func=draft_order)
    bp.add_url_rule("/order_del/<id>", view_func=order_del)

    bp.add_url_rule("/vouchers", view_func=vouchers)
    bp.add_url_rule(
        "/vouchers/create", view_func=vouchers_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule(
        "/vouchers/<id>/edit", view_func=vouchers_manage, methods=["GET", "POST"]
    )
    bp.add_url_rule("/sales", view_func=sales)
    bp.add_url_rule("/sales/create", view_func=sales_manage, methods=["GET", "POST"])
    bp.add_url_rule("/sales/<id>/edit", view_func=sales_manage, methods=["GET", "POST"])

    app.register_blueprint(bp, url_prefix="/dashboard")
