from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# URLs for the microservices
drone_URL = "http://drone:5000/drone"
scheduling_URL = "http://scheduling:5001/schedule"

# Simulated weather API response
def check_weather(location):
    # Simulating weather API with a dictionary
    # In a real implementation, you would call an actual weather API
    weather_conditions = {
        123456: "sunny",  # Store pickup location
        654321: "rainy",  # Some other location
        111111: "sunny"   # Another example location
    }
    
    condition = weather_conditions.get(location, "sunny")  # Default to sunny if location not found
    is_safe = condition.lower() != "rainy"  # Rainy is unsafe for drone flight
    
    return {
        "code": 200,
        "data": {
            "location": location,
            "weather_condition": condition,
            "is_safe": is_safe
        }
    }

@app.route("/check-condition", methods=['POST'])
def check_condition():
    if request.is_json:
        try:
            # Get the request data
            data = request.get_json()
            print("\nReceived a request to check conditions:", data)
            
            # 1 & 2. Check weather condition for the given location
            location = data.get("pickUpLocation")
            weather_result = check_weather(location)
            print("Weather result:", weather_result)
            
            if weather_result["code"] not in range(200, 300):
                return jsonify({
                    "code": weather_result["code"],
                    "message": "Failed to get weather information."
                }), weather_result["code"]
            
            # Check if weather is safe for flying
            if not weather_result["data"]["is_safe"]:
                return jsonify({
                    "code": 400,
                    "data": weather_result["data"],
                    "message": "Weather conditions not suitable for drone flight."
                }), 400
            
            # 4. Check for available drones
            drone_result = invoke_http(drone_URL + "s", method='GET')
            print("Drone result:", drone_result)
            
            if drone_result["code"] not in range(200, 300):
                return jsonify({
                    "code": drone_result["code"],
                    "message": "Failed to get drone information."
                }), drone_result["code"]
            
            # Find available drone
            available_drone = None
            for drone in drone_result["data"]["drones"]:
                if drone["status"] == "Available":
                    available_drone = drone
                    break
            
            # For testing purposes, if no drone is available, force one to be available
            if not available_drone and len(drone_result["data"]["drones"]) > 0:
                # Select the first drone and make it available
                selected_drone_id = drone_result["data"]["drones"][0]["Drone ID"]
                update_status = {
                    "status": "Available"
                }
                
                # Update drone status
                status_result = invoke_http(
                    f"{drone_URL}/{selected_drone_id}", method='PUT', json=update_status
                )
                print("Forced drone availability result:", status_result)
                
                if status_result["code"] in range(200, 300):
                    available_drone = status_result["data"]
            
            if not available_drone:
                return jsonify({
                    "code": 404,
                    "message": "No available drones found."
                }), 404
            
            # 6. Update the schedule with the available drone
            schedule_data = {
                "drone_id": available_drone["Drone ID"],
                "deliveryLocation": data.get("order_id", 1),  # Use order_id instead of the actual location
                "pickUpLocation": data.get("storeId", location),  # Use storeId if provided, fallback to location
                "weatherCheck": True  # Weather is safe as we've checked above
            }
            
            schedule_result = invoke_http(
                scheduling_URL, method='POST', json=schedule_data
            )
            print("Schedule result:", schedule_result)
            
            if schedule_result["code"] not in range(200, 300):
                return jsonify({
                    "code": schedule_result["code"],
                    "message": "Failed to create schedule: " + str(schedule_result["message"])
                }), schedule_result["code"]
            
            # 7. Return the scheduling details and weather condition
            return jsonify({
                "code": 200,
                "data": {
                    "schedule": schedule_result["data"],
                    "weather": weather_result["data"],
                    "drone": available_drone
                },
                "message": "Condition check successful, schedule created."
            })
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            
            return jsonify({
                "code": 500,
                "message": "condition_check.py internal error: " + ex_str
            }), 500
    
    # If reached here, not a JSON request
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) + " for checking drone and weather conditions...")
    app.run(host="0.0.0.0", port=5100, debug=True)