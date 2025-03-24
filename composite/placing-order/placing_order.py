import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)

# Base URLs for atomic services (change these to your actual URLs)
CUSTOMER_SERVICE_URL = 'http://customer-service:5005/customer'
ITEM_SERVICE_URL = 'http://item-service:5002/items'
ORDER_SERVICE_URL = 'http://order-service:5001/order'
PAYMENT_SERVICE_URL = 'http://payment-service:5003/pay'  # Placeholder URL

# Composite Service - Place an Order
@app.route("/place_order", methods=["POST"])
def place_order():
    try:
        # Step 1: Get customer details
        customer_id = request.json['customer_id']
        customer_response = requests.get(f"{CUSTOMER_SERVICE_URL}/{customer_id}")
        customer_data = customer_response.json()

        if customer_response.status_code != 200:
            return jsonify({"error": "Customer not found"}), 404

        # Step 2: Get item details
        cart_items = request.json['cart_item']
        item_details = []

        for item in cart_items:
            item_response = requests.get(f"{ITEM_SERVICE_URL}/{item['item_id']}")
            item_data = item_response.json()
            if item_response.status_code != 200:
                return jsonify({"error": f"Item {item['item_id']} not found"}), 404
            item_details.append(item_data)

        # Step 3: Create the order
        order_data = {
            "customer_id": customer_id,
            "cart_item": cart_items
        }
        order_response = requests.post(ORDER_SERVICE_URL, json=order_data)
        order_result = order_response.json()

        if order_response.status_code != 201:
            return jsonify({"error": "Failed to create order"}), 500

        # Step 4: Simulate Payment (Using Stripe or Placeholder)
        total_amount = sum([item['price'] * item['quantity'] for item in item_details])
        payment_data = {
            "customer_id": customer_id,
            "total_amount": total_amount
        }
        # Placeholder for Stripe API call (or other payment service)
        payment_response = requests.post(PAYMENT_SERVICE_URL, json=payment_data)
        payment_status = payment_response.json()

        if payment_response.status_code != 200 or payment_status.get("status") != "success":
            return jsonify({"error": "Payment failed"}), 500

        # Step 5: Return order confirmation
        return jsonify({
            "order_id": order_result['data']['order_id'],
            "customer": customer_data,
            "items": item_details,
            "payment_status": payment_status,
            "total_amount": total_amount
        }), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
