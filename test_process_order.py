import requests
import json
import sys
import os

# Force Docker mode since services are running in Docker
DOCKER_MODE = True
os.environ['DOCKER_MODE'] = 'true'
print(f"Running with DOCKER_MODE: {DOCKER_MODE}")

# Set the processing order URL based on environment
if DOCKER_MODE:
    PROCESSING_ORDER_URL = "http://localhost:5400/process_order"
else:
    PROCESSING_ORDER_URL = "http://localhost:5400/process_order"

def test_process_order(order_id=1):
    """Test the process_order endpoint"""
    
    print(f"\n=== TESTING PROCESS ORDER ENDPOINT ===")
    print(f"URL: {PROCESSING_ORDER_URL}")
    print(f"Order ID: {order_id}")
    print(f"DOCKER_MODE: {DOCKER_MODE}")
    
    try:
        # Prepare the request payload
        payload = {
            "order_id": order_id
        }
        
        # Send the request
        print(f"Sending request with payload: {payload}")
        response = requests.post(
            PROCESSING_ORDER_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Process the response
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            
            # Determine if the request was successful
            if response.status_code == 200:
                print("\n✅ ORDER PROCESSING SUCCESSFUL")
                return True
            else:
                print("\n❌ ORDER PROCESSING FAILED")
                if response_json.get("message"):
                    if "weather conditions not suitable" in response_json.get("message", "").lower():
                        print("Reason: Weather conditions are not suitable for drone flight")
                    elif "no available drones" in response_json.get("message", "").lower():
                        print("Reason: No available drones for delivery")
                    else:
                        print(f"Reason: {response_json.get('message')}")
                return False
        except ValueError:
            print(response.text)
            print("\n❌ ORDER PROCESSING FAILED: Could not parse JSON response")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # Process command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--docker':
            os.environ['DOCKER_MODE'] = 'true'
            print("Docker mode enabled via command line")
            order_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        else:
            try:
                order_id = int(sys.argv[1])
            except ValueError:
                print(f"Invalid order ID: {sys.argv[1]}")
                order_id = 1
    else:
        order_id = 1
    
    # Run the test
    test_process_order(order_id) 