from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# URLs for the microservices
order_URL = "http://order:5010/order"
store_URL = "http://store:5003/store"
drone_navigation_URL = "http://drone-navigation:5200/navigate-drone"
notification_URL = "http://notification:5300/notify" # This would be your notification service if implemented

@app.route("/health", methods=['GET'])
def health_check():
    return jsonify(
        {
            "message": "Processing Order Service is healthy."
        }
    ), 200

@app.route("/process_order", methods=['POST'])
def process_order():
    """
    Process a new order by:
    1. Getting delivery location from order details
    2. Getting pickup location from store
    3. Passing information to drone navigation service
    4. Updating order status
    5. Triggering customer notification
    """
    if request.is_json:
        try:
            # Get the request data
            data = request.get_json()
            print("\nReceived a request to process order:", data)
            
            # Extract order details
            order_id = data.get("order_id")
            
            if not order_id:
                return jsonify({
                    "code": 400,
                    "message": "Missing order_id in request"
                }), 400
                
            # Step 1: Get order details to retrieve delivery location
            print("Getting order details...")
            order_result = invoke_http(f"{order_URL}/{order_id}", method='GET')
            print("Order result:", order_result)
            
            if order_result["code"] != 200:
                return jsonify({
                    "code": order_result["code"],
                    "message": f"Failed to retrieve order information: {order_result.get('message', 'Unknown error')}"
                }), order_result["code"]
                
            # Extract delivery location from order
            delivery_location = order_result["data"].get("deliveryLocation") or order_result["data"].get("DeliveryLocation")
            customer_id = order_result["data"].get("customer_id") or order_result["data"].get("Customer_ID")
            
            if not delivery_location:
                return jsonify({
                    "code": 400,
                    "message": "Order does not have a delivery location"
                }), 400
                
            # Step 2: Get store information to retrieve pickup location
            # Assuming the first item in the order is used to determine the store
            if not order_result["data"]["order_item"]:
                # For testing purposes, use a hardcoded store ID
                print("Order does not have any items. Using default store ID 1 for testing.")
                store_id = 1
            else:
                first_item = order_result["data"]["order_item"][0]
                item_id = first_item["item_id"]
                
                # Get item details to find store ID
                item_result = invoke_http(f"http://item:5002/items/{item_id}", method='GET')
                if item_result["code"] != 200:
                    return jsonify({
                        "code": item_result["code"],
                        "message": f"Failed to retrieve item information: {item_result.get('message', 'Unknown error')}"
                    }), item_result["code"]
                    
                store_id = item_result["data"]["Store_ID"]
            
            # Get store pickup location
            store_result = invoke_http(f"{store_URL}/{store_id}", method='GET')
            print("Store result:", store_result)
            
            if "error" in store_result:
                return jsonify({
                    "code": 404,
                    "message": f"Failed to retrieve store information: {store_result.get('error', 'Unknown error')}"
                }), 404
                
            pickup_location = store_result["pickup_location"]
            
            # Step 3: Pass information to drone navigation service
            navigation_data = {
                "pickUpLocation": pickup_location,
                "storeId": store_id,
                "deliveryLocation": delivery_location,
                "order_id": order_id
            }
            
            print("Initiating drone navigation...")
            navigation_result = invoke_http(
                drone_navigation_URL, method='POST', json=navigation_data
            )
            print("Navigation result:", navigation_result)
            
            if navigation_result["code"] != 200:
                return jsonify({
                    "code": navigation_result["code"],
                    "message": f"Failed to initiate drone navigation: {navigation_result.get('message', 'Unknown error')}"
                }), navigation_result["code"]
                
            # Step 4: Update order status
            update_data = {
                "status": "SCHEDULED FOR DELIVERY"
            }
            
            update_result = invoke_http(
                f"{order_URL}/{order_id}", method='PUT', json=update_data
            )
            print("Update result:", update_result)
            
            if update_result["code"] != 200:
                return jsonify({
                    "code": update_result["code"],
                    "message": f"Failed to update order status: {update_result.get('message', 'Unknown error')}"
                }), update_result["code"]
                
            # Step 5: Send notification to customer (if notification service is implemented)
            try:
                notification_data = {
                    "customer_id": customer_id,
                    "message": f"Your order #{order_id} has been scheduled for delivery. A drone is on the way!",
                    "order_id": order_id
                }
                
                # Note: This is commented out because the notification service might not be implemented yet
                # notification_result = invoke_http(
                #     notification_URL, method='POST', json=notification_data
                # )
                # print("Notification result:", notification_result)
                
                print("Would send notification:", notification_data)
                
            except Exception as e:
                # Continue even if notification fails
                print(f"Notification failed but order processing will continue: {str(e)}")
                
            # Return complete order processing details
            return jsonify({
                "code": 200,
                "data": {
                    "order_details": order_result["data"],
                    "store_details": {
                        "store_id": store_id,
                        "pickup_location": pickup_location
                    },
                    "navigation_details": navigation_result["data"],
                    "status": "Order processing complete"
                },
                "message": "Order has been processed successfully and scheduled for delivery."
            })
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            
            return jsonify({
                "code": 500,
                "message": "processing_order.py internal error: " + ex_str
            }), 500
    
    # If reached here, not a JSON request
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) + " for processing orders...")
    app.run(host="0.0.0.0", port=5400, debug=True)
