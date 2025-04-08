import requests
import json
import sys
import os

# Check if running in Docker mode
DOCKER_MODE = os.environ.get('DOCKER_MODE', 'false').lower() == 'true'

# Set the condition check URL based on environment
if DOCKER_MODE:
    CONDITION_CHECK_URL = "http://condition-check:5100/check-condition"
else:
    CONDITION_CHECK_URL = "http://localhost:5100/check-condition"

def test_weather_check(pickup_location=1, delivery_location=1):
    """Test the weather check endpoint"""
    
    print(f"\n=== TESTING WEATHER CHECK SERVICE ===")
    print(f"URL: {CONDITION_CHECK_URL}")
    print(f"Pickup Location (Store ID): {pickup_location}")
    print(f"Delivery Location (Order ID): {delivery_location}")
    
    try:
        # Prepare the request payload
        weather_data = {
            "pickUpLocation": pickup_location,
            "deliveryLocation": delivery_location
        }
        
        # Send the request
        print(f"Sending request with payload: {weather_data}")
        response = requests.post(
            CONDITION_CHECK_URL,
            json=weather_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Process the response
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            
            # Determine if the weather check was successful
            if response.status_code == 200:
                print("\n✅ WEATHER CHECK PASSED: Conditions are suitable for drone flight")
                
                # Print the actual weather data from the response if available
                if isinstance(response_json, dict) and 'current_weather' in response_json:
                    weather = response_json['current_weather']
                    print("\nCurrent Weather Conditions:")
                    print(f"Temperature: {weather.get('temperature', 'N/A')}°C")
                    print(f"Wind Speed: {weather.get('wind_speed', 'N/A')} m/s")
                    print(f"Weather Description: {weather.get('description', 'N/A')}")
                return True
            else:
                print("\n❌ WEATHER CHECK FAILED: Conditions are NOT suitable for drone flight")
                if response_json.get("message"):
                    print(f"Reason: {response_json.get('message')}")
                return False
        except ValueError:
            print(response.text)
            print("\n❌ WEATHER CHECK FAILED: Could not parse JSON response")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # Process command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--docker':
        os.environ['DOCKER_MODE'] = 'true'
        print("Docker mode enabled via command line")
    
    # Parse location arguments if provided
    pickup = None
    delivery = None
    
    for i, arg in enumerate(sys.argv):
        if arg == '--pickup' and i+1 < len(sys.argv):
            try:
                pickup = int(sys.argv[i+1])
            except ValueError:
                print(f"Invalid pickup location: {sys.argv[i+1]}")
        elif arg == '--delivery' and i+1 < len(sys.argv):
            try:
                delivery = int(sys.argv[i+1])
            except ValueError:
                print(f"Invalid delivery location: {sys.argv[i+1]}")
    
    # Run the test with provided or default locations (using valid IDs)
    test_weather_check(
        pickup_location=pickup or 1,  # Using store_id 1 instead of location code
        delivery_location=delivery or 1  # Using order_id 1 instead of location code
    ) 