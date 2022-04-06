import paypalrestsdk
from flask import Flask, render_template, jsonify, request, redirect, Blueprint
from pluggy import HookimplMarker

impl = HookimplMarker("flaskshop")

def payment():

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://127.0.0.1:5000/payment/execute",
            "cancel_url": "http://127.0.0.1:5000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "sku": "12345",
                    "price": "3000000.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "3000000.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})


def test():
    print('hello')
    return render_template('Payment_success.html')


def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):

        print('Execute success!')
        success = True
    else:
        print('Execute error!')
    return jsonify(success)

@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("payment", __name__)
    print("fine")
    bp.add_url_rule("/payment", view_func=payment,methods=['POST'])
    bp.add_url_rule("/execute", view_func= execute,methods=['POST'])
    app.register_blueprint(bp, url_prefix="/payment")
