from flaskshop.product.models import (
    Category,
    ProductType,
    Product,
    ProductVariant,
    ProductImage,
    ProductAttribute,
    AttributeChoiceValue,
    ProductTypeAttributes,
    ProductTypeVariantAttributes,
    Collection,
    ProductCollection,
)
from flaskshop.public.models import MenuItem, Page
from flaskshop.account.models import User, UserAddress, Role, UserRole

def generate_menu_items(category: Category, menu_id=None, parent_id=None):
    menu_item, created = MenuItem.get_or_create(
        title=category.title,
        category_id=category.id,
        position=menu_id,
        parent_id=parent_id,
        background_img=category.background_img
    )

    for child in category.children:
         generate_menu_items(child, parent_id=menu_item.id)




def create_menus():
    categories = Category.query.all()
    for category in categories:
        if not category.parent_id:
             generate_menu_items(category, menu_id=1)


    yield "Created footer menu"
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
