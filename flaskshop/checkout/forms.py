from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField,  DateTimeField
from sqlalchemy.dialects.mysql import TINYINT
from wtforms import SelectField, RadioField, SubmitField
from wtforms.validators import DataRequired, NumberRange



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

class PaymentDeliveryForm(FlaskForm):
    shipping_methods = SelectField()
    payment_method = SelectField()

class CheckoutForm(FlaskForm):
    province = StringField()
    city = StringField()
    district = StringField()
    state= StringField()
    address = StringField()
    district=StringField()
    contact_name = StringField(validators=[DataRequired()])
    contact_phone = StringField(validators=[DataRequired()])
    pincode = StringField()
    email =StringField()
    submit = SubmitField()

