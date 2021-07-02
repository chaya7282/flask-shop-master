from flaskshop.product.models import (
    Category,
    Collection,
    ProductCollection,
)
from flaskshop.public.models import MenuItem, Page
from flaskshop.dashboard.models import DashboardMenu
from flaskshop.account.models import User, UserAddress, Role, UserRole
DASHBOARD_MENUS = [
    {"title": "קטלוג", "icon_cls": "fa-bandcamp"},
    {"title": "הזמנות", "endpoint": "orders", "icon_cls": "fa-cart-arrow-down"},
    {"title": "לקוחות", "endpoint": "users", "icon_cls": "fa-user"},
    {"title": "הנחות", "icon_cls": "fa-gratipay"},
    {"title": "CONFIGURATION", "endpoint": "config_index", "icon_cls": "fa-cog"},
    {"title": "מוצרים", "endpoint": "products", "parent_id": 1},
    {"title": "קטגוריות", "endpoint": "categories", "parent_id": 1},
    {"title": "אוספים", "endpoint": "collections", "parent_id": 1},
    {"title": "מכירות", "endpoint": "sales", "parent_id": 4},
    {"title": "קופונים", "endpoint": "vouchers", "parent_id": 4},
]

def create_dashboard_menus():
    DashboardMenu.drop_all()
    for item in DASHBOARD_MENUS:
        DashboardMenu.create(**item)


def generate_menu_items(category: Category, menu_id=None, parent_id=None):
    menu_item, created = MenuItem.get_or_create(
        title=category.title,
        category_id=category.id,
        position=menu_id,
        parent_id=category.parent_id,
    )

    for child in category.children:
         generate_menu_items(child, parent_id=menu_item.id)


def create_menus():
    menus=MenuItem.query.all()
    for _item in menus:
        _item.delete()
    categories = Category.query.all()
    for category in categories:
        if not category.parent_id:
             generate_menu_items(category, menu_id=1)

    collection = Collection.query.first()
    item, _ = MenuItem.get_or_create(title="Collections", position=2)
    for collection in Collection.query.all():
        MenuItem.get_or_create(
            title=collection.title, collection_id=collection.id, parent_id=item.id
        )

    item, _ = MenuItem.get_or_create(title="Saleor", position=2)
    page = Page.query.first()
    if page:
        MenuItem.get_or_create(title=page.title, page_id=page.id, parent_id=item.id)
    MenuItem.get_or_create(title="Style guide", url_="/style", parent_id=item.id)
