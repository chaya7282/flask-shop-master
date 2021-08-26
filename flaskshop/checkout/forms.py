from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField,  DateTimeField
from sqlalchemy.dialects.mysql import TINYINT
from wtforms import SelectField, RadioField

class NoteForm(FlaskForm):
    created_at = DateTimeField()
    delivery_time = DateTimeField()
    contact_phone = StringField()
    delivery_address = StringField()
    payment_method = SelectField("Status")
    delivery_method= SelectField("Status")
    note = TextAreaField("ADD A NOTE TO YOUR ORDER")


class VoucherForm(FlaskForm):
    code = StringField()

class CheckoutForm(FlaskForm):
    province = StringField()
    city = StringField()
    district = StringField()
    address = StringField()
    contact_name = StringField()
    contact_phone = StringField()
    delivery_method = SelectField("Status")

