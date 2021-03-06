from flask_wtf import FlaskForm as _FlaskForm
from flask_wtf import validators
from flask_wtf.file import FileField, FileAllowed,  FileRequired
from wtforms import (
    StringField,
    IntegerField,
    SubmitField,
    SelectField,
    RadioField,
    TextAreaField,
    BooleanField,
    PasswordField,
    FieldList,
    SelectMultipleField,
    FileField,
    FloatField,
    DecimalField,
    DateTimeField,
)
from wtforms.validators import DataRequired, optional, NumberRange, Length

from flaskshop.constant import SettingValueType
from flask import flash


class FlaskForm(_FlaskForm):
    def validate(self, extra_validators=None):
        self._errors = None
        success = True
        for name, field in self._fields.items():
            if field.type in (
                "SelectField",
                "SelectMultipleField",
                "RadioField",
                "FieldList",
            ):
                continue
            if extra_validators is not None and name in extra_validators:
                extra = extra_validators[name]
            else:
                extra = tuple()
            if not field.validate(self, extra):
                success = False
        return success

class BussinessForm(FlaskForm):
    address = StringField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired()])
    name =  StringField(validators=[DataRequired()])
    email = StringField()
    email_password = StringField()
    account_sid =  StringField("Twilo account sid")
    auth_token = StringField("Twilo auth token")
    Twilo_phone_Number =StringField("Twilo_phone_Number")
    payPal_SID = StringField("Pay Pal SID")
    payPal_Secret =StringField("Pay Pal Secret")

    image = StringField(validators=[DataRequired()])

class DashboardMenuForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    order = IntegerField(default=0)
    endpoint = StringField()
    icon_cls = StringField()
    parent_id = SelectField("Parent")
    submit = SubmitField()

class OrderStatusForm(FlaskForm):
    status= SelectField("Status")



class SiteMenuForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    order = IntegerField(default=0)
    url_ = StringField("Url")
    parent_id = SelectField("Parent")
    position = RadioField(choices=[(0, "none"), (1, "top"), (2, "bottom")], default=0)
    category_id = SelectField("Category")
    collection_id = SelectField("Collection")
    page_id = SelectField("Page")
    submit = SubmitField()


class SitePageForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    slug = StringField()
    content = TextAreaField()
    is_visible = BooleanField(default=True)
    submit = SubmitField()


class SiteConfigForm(FlaskForm):
    header_text = StringField(validators=[DataRequired()])
    description = TextAreaField()
    submit = SubmitField()

class UserForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    password = PasswordField()
    is_active = BooleanField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    role = SelectField("Role", default=0)
    submit = SubmitField()



class FileImportForm(FlaskForm):
    xls_file = FileField(validators=[ FileRequired(), FileAllowed(['xls','xlsx'], 'xls only!')])
    DataType = SelectMultipleField("Data Type",choices=[(0,'product'), (1,'Categories')],)
    submit = SubmitField()
class FileExportForm(FlaskForm):

    submit = SubmitField()
class UserAddressForm(FlaskForm):
    province = StringField()
    city = StringField()
    district = StringField()
    address = StringField()
    contact_name = StringField()
    contact_phone = StringField()
    pincode = StringField()
    email = StringField()

    submit = SubmitField()


class AttributeForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    values = FieldList(StringField("Value"))
    types = SelectMultipleField("Product Types")
    background_imgs = FieldList(FileField('file'))

    submit = SubmitField()


class CollectionForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    products = SelectMultipleField()
    background_img = StringField("Current Image")
    bgimg_file = FileField("Upload")
    submit = SubmitField()


class CategoryForm(FlaskForm):
    title = StringField(validators=[DataRequired(), Length(min=1, max=40)])
    is_active = BooleanField("Is-Active", default=True)
    parent_id = SelectField("Parent", default=0)
    current_img = FileField()
    background_img = FileField(validators=[FileAllowed(['jpg', 'png','jpeg','png'])])
    description = TextAreaField("Description")
    submit = SubmitField()


class ProductTypeForm(FlaskForm):
    title = StringField(validators=[DataRequired(), Length(min=6, max=80)])
    has_variants = BooleanField("has_variants",default=False)
    has_attributes= BooleanField("has_attributes",default=False)
    is_shipping_required = BooleanField("is_shipping_required",default=True)
    product_attributes = SelectMultipleField("product_attributes")

    variant_attr_id = SelectField("Variant Attributes")
    submit = SubmitField()


class ProductForm(FlaskForm):
    title = StringField("title",validators=[DataRequired(), Length(min=6, max=100)])
    discount_price = DecimalField("Before Sale",default=0.00, validators=[NumberRange(min=0, max=10000)])
    basic_price = DecimalField("Product Price",default=0.00, validators=[DataRequired(), NumberRange(min=0, max=10000)])

    on_sale = BooleanField("On Sale",default=False)
    is_active = BooleanField("Is-Active",default=True)
    is_featured = BooleanField("Special", default=False)
    in_front_banner=BooleanField("In front banner", default=False)
    active= BooleanField("", default=False)
    need_check_stock= BooleanField("need check stock", default=False)
    rating = FloatField(default=0)
    sold_count = IntegerField(default=0)
    review_count = IntegerField(default=0)
    category_id = SelectField("category",validators=[DataRequired()])
    description = TextAreaField(default=0)
    background_img = StringField("Next Image",default=0)
    current_img = StringField("Current Image")
    images = FileField("image",validators=[FileAllowed(['png','jpg','jpeg'], 'png,jpg,jpeg only')],default=0)
    attributes = FieldList(SelectField())
    variant_attributes = SelectMultipleField()
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(ProductForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super( ProductForm, self).validate()
        if not initial_validation:
            return False

        if self.category_id.data == "None":
            flash("Try To add categories First",'danger')
            return False
        return True

class ProductCreateForm(FlaskForm):
    product_type_id = SelectField("?????? ?????? ????????", default=1)
    submit = SubmitField()


class VariantForm(FlaskForm):
    sku_id = IntegerField(
        "SKU", validators=[DataRequired(), NumberRange(min=1, max=9999)]
    )
    title = StringField(validators=[DataRequired()])
    price_override = DecimalField(default=0.00, validators=[NumberRange(min=0)])
    quantity = IntegerField(default=0, validators=[NumberRange(min=0)])
    submit = SubmitField()


class ShippingMethodForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    price = DecimalField(default=0.00, validators=[NumberRange(min=0)])
    address_needed = BooleanField("address needed",default=True)
    submit = SubmitField()


class VoucherForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    type_ = SelectField(default=1)
    code = StringField(validators=[DataRequired()])
    usage_limit = IntegerField(
        description="how many times can be used", validators=[optional()]
    )
    used = IntegerField(default=0)
    validity_period = StringField()
    discount_value_type = SelectField(default=1)
    discount_value = DecimalField(default=0.00)
    limit = IntegerField(validators=[optional()])
    category_id = SelectField(
        "Category", description="when type is category, need to select"
    )
    product_id = SelectField(
        "Product", description="when type is product, need to select"
    )
    submit = SubmitField()


class SaleForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    discount_value_type = SelectField(default=1)
    discount_value = DecimalField(default=0.00)
    categories = SelectMultipleField("Category")
    products = SelectMultipleField("Product")
    submit = SubmitField()


def generate_settings_form(settings):
    """Generates a settings form which includes field validation
    based on our Setting Schema."""

    class SettingsForm(FlaskForm):
        pass

    # now parse the settings in this group
    for setting in settings:
        field_validators = []

        if setting.value_type in {SettingValueType.integer, SettingValueType.float}:
            validator_class = NumberRange
        elif setting.value_type == SettingValueType.string:
            validator_class = Length

        # generate the validators
        if setting.extra:
            if "min" in setting.extra:
                # Min number validator
                field_validators.append(validator_class(min=setting.extra["min"]))

            if "max" in setting.extra:
                # Max number validator
                field_validators.append(validator_class(max=setting.extra["max"]))

        # Generate the fields based on value_type
        # IntegerField
        if setting.value_type == SettingValueType.integer:
            setattr(
                SettingsForm,
                setting.key,
                IntegerField(
                    setting.name,
                    validators=field_validators,
                    description=setting.description,
                ),
            )
        # FloatField
        elif setting.value_type == SettingValueType.float:
            setattr(
                SettingsForm,
                setting.key,
                FloatField(
                    setting.name,
                    validators=field_validators,
                    description=setting.description,
                ),
            )

        # TextField
        elif setting.value_type == SettingValueType.string:
            setattr(
                SettingsForm,
                setting.key,
                StringField(
                    setting.name,
                    validators=field_validators,
                    description=setting.description,
                ),
            )

        # SelectMultipleField
        elif setting.value_type == SettingValueType.selectmultiple:
            # if no coerce is found, it will fallback to unicode
            if "coerce" in setting.extra:
                coerce_to = setting.extra["coerce"]
            else:
                coerce_to = text_type

            setattr(
                SettingsForm,
                setting.key,
                SelectMultipleField(
                    setting.name,
                    choices=setting.extra["choices"](),
                    coerce=coerce_to,
                    description=setting.description,
                ),
            )

        # SelectField
        elif setting.value_type == SettingValueType.select:
            # if no coerce is found, it will fallback to unicode
            if "coerce" in setting.extra:
                coerce_to = setting.extra["coerce"]
            else:
                coerce_to = text_type

            setattr(
                SettingsForm,
                setting.key,
                SelectField(
                    setting.name,
                    coerce=coerce_to,
                    choices=setting.extra["choices"](),
                    description=setting.description,
                ),
            )

        # BooleanField
        elif setting.value_type == SettingValueType.boolean:
            setattr(
                SettingsForm,
                setting.key,
                BooleanField(setting.name, description=setting.description),
            )

    return SettingsForm
