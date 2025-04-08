from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# URLs for the microservices
condition_check_URL = "http://condition-check:5100/check-condition"
drone_URL = "http://drone:5006/drone"

@app.route("/navigate-drone", methods=['POST'])
def navigate_drone():
    if request.is_json:
        try:
            # Get the request data
            data = request.get_json()
            print("\nReceived a request for drone navigation:", data)
            
            # 1. Check for weather condition and drone status
            condition_result = invoke_http(
                condition_check_URL, method='POST', json=data
            )
            print("Condition check result:", condition_result)
            
            if condition_result["code"] not in range(200, 300):
                return jsonify({
                    "code": condition_result["code"],
                    "message": "Failed condition check: " + str(condition_result.get("message", "Unknown error"))
                }), condition_result["code"]
            
            # Get the drone ID from the condition check response
            drone_id = condition_result["data"]["drone"]['Drone ID']
            
            # Update drone status to "On Delivery"
            update_status = {
                "status": "On Delivery"
            }
            
            status_result = invoke_http(
                f"{drone_URL}/{drone_id}", method='PUT', json=update_status
            )
            print("Status update result:", status_result)
            
            if status_result["code"] not in range(200, 300):
                return jsonify({
                    "code": status_result["code"],
                    "message": "Failed to update drone status: " + str(status_result.get("message", "Unknown error"))
                }), status_result["code"]
            
            # Return the navigation details with weather condition and drone status
            return jsonify({
                "code": 200,
                "data": {
                    "condition_check": condition_result["data"],
                    "drone_status": status_result["data"],
                    "navigation_message": f"Drone {drone_id} is now navigating to the pickup location."
                },
                "message": "Drone navigation initiated successfully."
            })
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            
            return jsonify({
                "code": 500,
                "message": "drone_navigation.py internal error: " + ex_str
            }), 500
    
    # If reached here, not a JSON request
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) + " for drone navigation...")
    app.run(host="0.0.0.0", port=5200, debug=True)