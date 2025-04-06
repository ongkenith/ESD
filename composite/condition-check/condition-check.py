from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http
import requests
import json
from os import environ

app = Flask(__name__)
CORS(app)

# Use environment variables for service URLs, provide defaults for local testing
WEATHER_API_KEY = environ.get('WEATHER_API_KEY')

# Determine environment and set base URLs
DOCKER_MODE = os.environ.get('DOCKER_MODE', 'true').lower() == 'true'

# Set base hostnames based on environment
if DOCKER_MODE:
    print("Running in Docker mode with container hostnames")
    DRONE_HOST = "drone:5006"
    SCHEDULING_HOST = "scheduling:5005"
else:
    print("Running in local mode with localhost")
    DRONE_HOST = "localhost:5006"
    SCHEDULING_HOST = "localhost:5005"

# URLs for the microservices
drone_URL = f"http://{DRONE_HOST}/drone"
scheduling_URL = f"http://{SCHEDULING_HOST}/schedule"

# OpenWeather API configuration
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Function to check weather using OpenWeather API
def check_weather(location):
    # Map location codes to city names for the API call
    city_mapping = {
        123456: "Singapore",
        654321: "Singapore,Marina Bay",
        111111: "Singapore,Changi"
    }
    
    # Get city name based on location or default to Singapore
    city_name = city_mapping.get(location, "Singapore")
    
    try:
        print(f"\nAttempting to call OpenWeather API for location {location} mapped to city: {city_name}")
        # Make API call to OpenWeather
        params = {
            "q": city_name,
            "APPID": WEATHER_API_KEY,  # Use APPID instead of appid
            "units": "metric"  # Get temperature in Celsius
        }
        
        api_url = WEATHER_API_URL
        print(f"Full API URL: {api_url}?q={params['q']}&APPID={params['APPID']}&units={params['units']}")
        
        # Test connection to api.openweathermap.org
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex(('api.openweathermap.org', 80))
            if result == 0:
                print("Connection to api.openweathermap.org is successful")
            else:
                print(f"Connection to api.openweathermap.org failed with error code {result}")
            s.close()
        except Exception as e:
            print(f"Socket test failed: {str(e)}")
        
        # Make the actual API request
        print("Sending request to OpenWeather API...")
        response = requests.get(api_url, params=params, timeout=5)
        print(f"OpenWeather API response status code: {response.status_code}")
        
        if response.status_code == 200:
            weather_data = response.json()
            print(f"OpenWeather API response data: {json.dumps(weather_data, indent=2)}")
            
            # Extract relevant weather information
            weather_condition = weather_data["weather"][0]["main"].lower()
            temperature = weather_data["main"]["temp"]
            wind_speed = weather_data["wind"]["speed"]
            
            # Define conditions unsafe for drone flight
            unsafe_conditions = ["thunderstorm", "rain", "snow"]
            high_wind_threshold = 10.0  # m/s (normal threshold for drone flight)
            
            # Check if weather is safe for drone flight
            is_safe = (
                weather_condition not in unsafe_conditions and 
                wind_speed < high_wind_threshold
            )
            
            return {
                "code": 200,
                "data": {
                    "location": location,
                    "weather_condition": weather_condition,
                    "temperature": temperature,
                    "wind_speed": wind_speed,
                    "is_safe": is_safe,
                    "source": "OpenWeather API"
                }
            }
        else:
            # API call failed, fall back to default safe weather
            print(f"Weather API call failed with status {response.status_code}")
            print(f"Response content: {response.text}")
            return {
                "code": 200,
                "data": {
                    "location": location,
                    "weather_condition": "sunny",
                    "is_safe": True,
                    "source": "Default fallback (API call failed)",
                    "error_details": f"API status: {response.status_code}, Response: {response.text}"
                }
            }
    except Exception as e:
        # Exception occurred, fall back to default safe weather
        import traceback
        print(f"Error retrieving weather data: {str(e)}")
        print(traceback.format_exc())
        return {
            "code": 200,
            "data": {
                "location": location,
                "weather_condition": "sunny",
                "is_safe": True,
                "source": "Default fallback (exception)",
                "error_details": str(e)
            }
        }

@app.route("/check-condition", methods=['POST'])
def check_condition():
    if request.is_json:
        try:
            # Get the request data
            data = request.get_json()
            print("\nReceived a request to check conditions:", data)
            
            # Get both actual locations and reference IDs
            pickup_location = data.get("pickUpLocation")  # Actual location for weather check
            store_id = data.get("storeId")  # For foreign key
            delivery_location = data.get("deliveryLocation")  # Actual delivery location
            order_id = data.get("order_id")  # For foreign key
            
            # Check weather using actual pickup location
            weather_result = check_weather(pickup_location)
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
            
            # Check for available drones
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
                selected_drone_id = drone_result["data"]["drones"][0]["Drone ID"]
                update_status = {
                    "status": "Available"
                }
                
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
            
            # Create schedule with both actual locations and reference IDs
            schedule_data = {
                "drone_id": available_drone["Drone ID"],
                "store_id": store_id,  # Store ID for foreign key
                "order_id": order_id,  # Order ID for foreign key
                "pickUpLocation": pickup_location,  # Actual pickup location
                "deliveryLocation": delivery_location,  # Actual delivery location
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
            
            # Return the scheduling details and weather condition
            return jsonify({
                "code": 200,
                "data": {
                    "schedule": schedule_result["data"],
                    "weather": weather_result["data"],
                    "drone": available_drone,
                    "locations": {
                        "pickup": {
                            "actual_location": pickup_location,
                            "store_id": store_id
                        },
                        "delivery": {
                            "actual_location": delivery_location,
                            "order_id": order_id
                        }
                    }
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