# Flask application to demo accepting payments via PayPal
# using the rest sdk for Python

from flask import Flask, render_template, request, jsonify, abort, make_response
import paypalrestsdk
import json

app = Flask(__name__)

# Get MODE, CLIENT_ID and CLIENT_SECRET from config file
app.config.from_envvar('CONFIG')
paypalrestsdk.configure({
    "mode": app.config['MODE'],
    "client_id": app.config['CLIENT_ID'],
    "client_secret": app.config['CLIENT_SECRET']
})


@app.route("/")
def credit_card_form():
    return render_template("card.html")


@app.route("/create_payment", methods=["POST"])
def create_payment():
    '''
    Set intent as sale for immediate payment
    '''
    print
    request.form
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "credit_card",
            "funding_instruments": [{
                "credit_card": {
                    "type": "visa",
                    "number": request.form["number"],
                    "expire_month": request.form["expire_month"],
                    "expire_year": request.form["expire_year"],
                    "cvv2": request.form["cvv2"]
                }
            }]
        },
        "transactions": [{
            "amount": {
                "total": "12",
                "currency": "USD"
            },
            "description": "creating a direct payment with credit card"
        }]
    })
    if payment.create():
        return "<h1>Payment {0} created successfully</h1>".format(payment.id)
    else:
        return "<h1>Error while creating payment: {0}</h1>".format(payment.error)


@app.route('/find_payment', methods=['POST'])
def find_payment():
    if not request.json or not 'proof_of_payment' in request.json:
        abort(400)
    proof = request.json.get('proof_of_payment')

    if 'rest_api' not in proof or proof.get('rest_api').get('state') != 'approved':
        abort(400)
    payment_id = proof.get('rest_api').get('payment_id')
    print
    payment_id

    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        print
        payment
        if payment.state != 'approved':
            abort(400)

        # Verify that payment contains a transaction with
        # 	1. An amount with total and currency that match request from client sdk
        amount_client = request.json.get('payment').get('amount')
        currency_client = request.json.get('payment').get('currency_code')
        print
        amount_client

        for transaction in payment.transactions:
            amount_server = transaction.amount.total
            currency_server = transaction.amount.currency

            if (amount_server == amount_client) and (currency_client == currency_server):
                sale_state = transaction.related_resources[0].sale.state
                break
        #	2. A sale that is completed
        print
        amount_client
        if (amount_server != amount_client) and (currency_client != currency_server):
            abort(400)
        if sale_state != 'completed':
            abort(400)
        return jsonify({"status": "verified"}), 201

    except paypalrestsdk.ResourceNotFound as error:
        abort(400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found on the server, sorry!'}), 404)


if __name__ == '__main__':
    app.run(debug=True)