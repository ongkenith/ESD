import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
CORS(app) # Enable CORS for better cross-origin support

# Use environment variables for service URLs, provide defaults for local testing
CUSTOMER_SERVICE_URL = environ.get('CUSTOMER_URL', 'http://localhost:5001') + '/customer'
ITEM_SERVICE_URL = environ.get('ITEM_URL', 'http://localhost:5002') + '/items'
ORDER_SERVICE_URL = environ.get('ORDER_URL', 'http://localhost:5004') + '/order'
PROCESSING_ORDER_URL = environ.get('PROCESSING_ORDER_URL', 'http://localhost:5400') + '/process_order' # Assuming '/process_order' endpoint
# PAYMENT_SERVICE_URL = environ.get('PAYMENT_URL', 'http://localhost:500X') + '/pay' # Placeholder

# Health check endpoint
@app.route("/health")
def health_check():
    return jsonify(status="healthy", message="Placing Order Service is running.")

# Composite Service - Place an Order
@app.route("/place_order", methods=["POST"])
def place_order():
    app.logger.info("Received place_order request")
    try:
        data = request.get_json()
        if not data or 'Customer_ID' not in data or 'cart_item' not in data or 'delivery_location' not in data:
            app.logger.error("Invalid JSON payload received")
            return jsonify({"error": "Invalid JSON payload", "data": data}), 400
        
        customer_id = data['Customer_ID']
        delivery_location = data['delivery_location']
        cart_items = data['cart_item']
        app.logger.info(f"Processing order for customer_id: {customer_id}")

        # Step 1: Get customer details
        customer_url = f"{CUSTOMER_SERVICE_URL}/{customer_id}"
        app.logger.info(f"Calling Customer Service: {customer_url}")
        try:
            customer_response = requests.get(customer_url)
            customer_response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
            customer_data = customer_response.json()
            app.logger.info(f"Customer data received: {customer_data}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Customer service request failed: {e}")
            return jsonify({"error": f"Failed to retrieve customer details: {e}"}), 503 # Service Unavailable
        except ValueError: # Includes JSONDecodeError
             app.logger.error(f"Failed to decode customer service response: {customer_response.text}")
             return jsonify({"error": "Invalid response from customer service"}), 502 # Bad Gateway

        # Step 2: Get item details & calculate total amount (assuming price is in item details)
        item_details_full = []
        total_amount = 0
        for item_req in cart_items:
            item_id = item_req.get('item_id')
            quantity = item_req.get('quantity')
            if item_id is None or quantity is None:
                 app.logger.error(f"Invalid item format in cart: {item_req}")
                 return jsonify({"error": "Invalid item format in cart"}), 400

            item_url = f"{ITEM_SERVICE_URL}/{item_id}"
            app.logger.info(f"Calling Item Service: {item_url}")
            try:
                item_response = requests.get(item_url)
                item_response.raise_for_status()
                item_data = item_response.json()
                app.logger.info(f"Item data received: {item_data}")
                
                # Assuming item_data has 'price'
                price = item_data["data"]['Price']
                if price is None:
                     app.logger.error(f"Price not found for item {item_id}: {item_data}")
                     return jsonify({"error": f"Price not found for item {item_id}"}), 500
                
                total_amount += price * quantity
                item_details_full.append({
                    "item_id": item_id,
                    "name": item_data.get('name', 'N/A'), # Get name if available
                    "price": price,
                    "quantity": quantity
                })

            except requests.exceptions.RequestException as e:
                app.logger.error(f"Item service request failed for item {item_id}: {e}")
                return jsonify({"error": f"Failed to retrieve details for item {item_id}: {e}"}), 503
            except ValueError:
                 app.logger.error(f"Failed to decode item service response: {item_response.text}")
                 return jsonify({"error": f"Invalid response from item service for item {item_id}"}), 502
            except TypeError:
                 app.logger.error(f"Error processing item price or quantity for item {item_id}: price={price}, quantity={quantity}")
                 return jsonify({"error": f"Error calculating price for item {item_id}"}), 500

        # Step 3: Create the order (Send data to Order Service)
        order_payload = {
            "Customer_ID": customer_id,
            "cart_item": cart_items, # Send original cart items as Order service might need quantity
            "total_amount": total_amount, # Send calculated total amount
            "delivery_location": delivery_location
        }
        app.logger.info(f"Calling Order Service: {ORDER_SERVICE_URL} with payload: {order_payload}")
        try:
            order_response = requests.post(ORDER_SERVICE_URL, json=order_payload)
            order_response.raise_for_status()
            order_result = order_response.json()
            app.logger.info(f"Order service response: {order_result}")

            # Check if order service response contains expected data (adjust based on actual response)
            if 'data' not in order_result or 'order_id' not in order_result['data']:
                 app.logger.error(f"Unexpected response format from order service: {order_result}")
                 return jsonify({"error": "Invalid response format from order service"}), 502
            
            order_id = order_result['data']['order_id']

        except requests.exceptions.RequestException as e:
            # Log the specific error and response text if available
            response_text = e.response.text if e.response else "No response content"
            app.logger.error(f"Order service request failed: {e}. Response: {response_text}")
            # Return a more specific error based on status code if possible
            status_code = e.response.status_code if e.response else 503
            return jsonify({"error": f"Failed to create order: {response_text}"}), status_code
        except ValueError: # Includes JSONDecodeError
             app.logger.error(f"Failed to decode order service response: {order_response.text}")
             return jsonify({"error": "Invalid response from order service"}), 502

        # Step 4: Call Processing Order Service
        processing_payload = { "order_id": order_id } # Send order_id to processing service
        app.logger.info(f"Calling Processing Order Service: {PROCESSING_ORDER_URL} for order_id: {order_id}")
        try:
            headers = {'Content-Type': 'application/json'} # Define headers
            processing_response = requests.post(PROCESSING_ORDER_URL, json=processing_payload, headers=headers) # Add headers
            processing_response.raise_for_status() # Check for HTTP errors
            processing_result = processing_response.json()
            app.logger.info(f"Processing order service response: {processing_result}")
            # Optional: Check processing_result for success indicator if needed

        except requests.exceptions.RequestException as e:
            # Log the specific error and response text if available
            proc_response_text = e.response.text if e.response else "No response content"
            app.logger.error(f"Processing order service request failed: {e}. Response: {proc_response_text}")
            # Decide how critical this is. Maybe the order is created but processing failed.
            # Return a partial success or a specific error?
            # For now, let's return an error indicating processing failed.
            proc_status_code = e.response.status_code if e.response else 503
            return jsonify({
                "error": f"Order created (ID: {order_id}) but failed to initiate processing: {proc_response_text}",
                 "order_id": order_id # Still return order_id if created
                 }), proc_status_code
        except ValueError: # Includes JSONDecodeError
             app.logger.error(f"Failed to decode processing order service response: {processing_response.text}")
             return jsonify({"error": f"Order created (ID: {order_id}) but received invalid response from processing service", "order_id": order_id}), 502

        # Step 5: Simulate Payment (Placeholder - commented out)
        # app.logger.info(f"Simulating payment for order {order_id} with amount {total_amount}")
        # payment_data = {
        #     "customer_id": customer_id,
        #     "order_id": order_id,
        #     "total_amount": total_amount
        # }
        # try:
        #     payment_response = requests.post(PAYMENT_SERVICE_URL, json=payment_data)
        #     payment_response.raise_for_status()
        #     payment_status = payment_response.json()
        #     if payment_status.get("status") != "success":
        #         app.logger.error(f"Payment failed: {payment_status}")
        #         # Consider how to handle payment failure (e.g., cancel order?)
        #         return jsonify({"error": "Payment failed", "details": payment_status}), 500
        #     app.logger.info(f"Payment successful: {payment_status}")
        # except requests.exceptions.RequestException as e:
        #     app.logger.error(f"Payment service request failed: {e}")
        #     return jsonify({"error": f"Payment service communication error: {e}"}), 503
        # except ValueError:
        #      app.logger.error(f"Failed to decode payment service response: {payment_response.text}")
        #      return jsonify({"error": "Invalid response from payment service"}), 502

        # Step 6: Return order confirmation (simplified as payment is placeholder)
        app.logger.info(f"Order {order_id} created and sent for processing for customer {customer_id}")
        return jsonify({
            "message": "Order created successfully and sent for processing", # Updated message
            "order_id": order_id,
            "customer_details": customer_data, # Customer details fetched earlier
            "items_ordered": item_details_full, # Detailed items with price/quantity
            "processing_status": processing_result, # Include response from processing service
            "total_amount": total_amount
        }), 201 # Use 201 Created status

    except Exception as e:
        app.logger.exception(f"An unexpected error occurred: {e}") # Log full traceback
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == "__main__":
    # Basic logging configuration
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting Placing Order Service...")
    # Use port 5500 as defined in Dockerfile/docker-compose
    app.run(host="0.0.0.0", port=5500, debug=True) # Set debug=False for production
