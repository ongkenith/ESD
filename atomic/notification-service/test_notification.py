from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys

app = Flask(__name__)
CORS(app)

# Function to simulate sending SMS
def send_sms(phone_number, message):
    print(f"Simulating SMS sent to {phone_number}: {message}")
    # In a real implementation, you would integrate with an SMS provider like Twilio
    return True

# Function to get customer contact info
def get_customer_contact(customer_id):
    # This would typically come from a database lookup
    # For now, we'll simulate it
    customer_data = {
        1: {"name": "Tina", "phone": "91234567", "email": "tina@email.com"},
        2: {"name": "Kenny", "phone": "92345678", "email": "kenny@email.com"},
        3: {"name": "Jordan", "phone": "93456789", "email": "jordan@email.com"},
        4: {"name": "Jasdev", "phone": "94567890", "email": "jasdev@email.com"},
        5: {"name": "Zhengjie", "phone": "95678901", "email": "zhengjie@email.com"},
        6: {"name": "Deshaun", "phone": "96789012", "email": "deshaun@email.com"}
    }
    return customer_data.get(customer_id, {"name": "Unknown", "phone": "00000000", "email": "unknown@email.com"})

# REST API endpoint for direct notifications (can be used for testing)
@app.route("/notify", methods=['POST'])
def notify():
    if request.is_json:
        try:
            data = request.get_json()
            print("\nReceived a direct notification request:", data)
            
            customer_id = data.get('customer_id')
            message = data.get('message')
            order_id = data.get('order_id')
            
            if not all([customer_id, message, order_id]):
                return jsonify({
                    "code": 400,
                    "message": "Missing required fields (customer_id, message, order_id)"
                }), 400
                
            customer = get_customer_contact(customer_id)
            phone_number = customer.get('phone')
            
            if not phone_number:
                return jsonify({
                    "code": 404,
                    "message": f"No phone number found for customer ID {customer_id}"
                }), 404
                
            # Send the SMS
            send_success = send_sms(phone_number, message)
            
            if send_success:
                return jsonify({
                    "code": 200,
                    "data": {
                        "customer_id": customer_id,
                        "customer_name": customer.get('name'),
                        "phone_number": phone_number,
                        "message": message,
                        "order_id": order_id
                    },
                    "message": "Notification sent successfully"
                }), 200
            else:
                return jsonify({
                    "code": 500,
                    "message": "Failed to send notification"
                }), 500
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            
            return jsonify({
                "code": 500,
                "message": "notification.py internal error: " + ex_str
            }), 500
    
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

# Health check endpoint
@app.route("/health", methods=['GET'])
def health_check():
    return jsonify(
        {
            "message": "Notification Service is healthy."
        }
    ), 200

if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) + " for testing notifications...")
    app.run(host="0.0.0.0", port=5300, debug=True) 