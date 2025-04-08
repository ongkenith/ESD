import requests
import time
from os import environ
import sys

# Connect directly to drone service in Docker - no need to go through Kong
DRONE_URL = "http://localhost:5006/drones"

def reset_all_drones():
    try:
        print(f"Getting drones from: {DRONE_URL}")
        response = requests.get(DRONE_URL)
        
        if response.status_code != 200:
            print(f"Error getting drones: {response.text}")
            return False
            
        data = response.json()
        
        # Handle different response formats
        if "data" in data and "drones" in data["data"]:
            drones = data["data"]["drones"]
        elif "drones" in data:
            drones = data["drones"]
        else:
            print(f"Unexpected response format: {data}")
            return False
        
        print(f"Found {len(drones)} drones")
        
        # 2. Reset each drone to Available
        success_count = 0
        for drone in drones:
            # Handle different drone ID field names
            drone_id = drone.get("Drone ID") or drone.get("droneID") or drone.get("id")
            
            if not drone_id:
                print(f"Could not determine drone ID from: {drone}")
                continue
                
            # Update URL for individual drone
            update_url = f"http://localhost:5006/drone/{drone_id}"
            print(f"Updating drone {drone_id} at: {update_url}")
            
            update_response = requests.put(
                update_url,
                json={"status": "Available"}
            )
            
            if update_response.status_code == 200:
                success_count += 1
                print(f"Reset drone {drone_id} to Available")
            else:
                print(f"Failed to reset drone {drone_id}: {update_response.status_code} - {update_response.text}")
        
        print(f"\nSuccessfully reset {success_count} out of {len(drones)} drones")
        return success_count > 0

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    print("Waiting 3 seconds before resetting drones...")
    time.sleep(3)  # Wait 3 seconds
    
    print("Starting drone reset process...")
    retry_count = 3
    
    for attempt in range(retry_count):
        print(f"Attempt {attempt+1} of {retry_count}")
        if reset_all_drones():
            print("Successfully reset drones. You can now proceed with checkout.")
            break
        elif attempt < retry_count - 1:
            print(f"Retrying in 3 seconds...")
            time.sleep(3)
        else:
            print("Failed to reset drones after multiple attempts. Please try again or contact support.")

if __name__ == "__main__":
    main() 