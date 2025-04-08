import requests
import json
import time
import sys
import os

def check_service_health(service_name, port, endpoint="/health", max_retries=5):
    """Check if a service is healthy by making a request to its health endpoint"""
    url = f"http://localhost:{port}{endpoint}"
    print(f"Checking health of {service_name} at {url}")
    
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"{service_name} is healthy!")
                return True
            else:
                print(f"{service_name} returned status code {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {i+1}/{max_retries}: {service_name} not responding: {str(e)}")
        
        if i < max_retries - 1:
            wait_time = 2 ** i  # Exponential backoff
            print(f"Waiting {wait_time} seconds before next attempt...")
            time.sleep(wait_time)
    
    print(f"{service_name} is not healthy after {max_retries} attempts")
    return False

def test_order_service(order_id=1):
    """Test if the order service is responding correctly"""
    url = f"http://localhost:5004/order/{order_id}"
    print(f"Testing order service at {url}")
    
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_process_order_direct(order_id=1):
    """Test the direct connection to each service that process_order uses"""
    services_to_check = [
        ("Order Service", 5004, f"/order/{order_id}"),
        ("Store Service", 5003, "/store/1"),
        ("Item Service", 5002, "/items/1"),
        ("Drone Navigation", 5200, "/health"),
        ("Notification", 5300, "/health"),
        ("RabbitMQ", 15672, "/api/overview")  # RabbitMQ management API
    ]
    
    results = {}
    
    for service_name, port, endpoint in services_to_check:
        url = f"http://localhost:{port}{endpoint}"
        print(f"\nTesting {service_name} at {url}")
        
        try:
            # Special case for RabbitMQ which requires auth
            if service_name == "RabbitMQ":
                response = requests.get(url, auth=('guest', 'guest'))
            else:
                response = requests.get(url)
                
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"{service_name} is responsive")
                results[service_name] = True
            else:
                print(f"{service_name} returned an error: {response.text}")
                results[service_name] = False
        except Exception as e:
            print(f"{service_name} error: {str(e)}")
            results[service_name] = False
    
    # Print summary
    print("\n=== SERVICE CHECK SUMMARY ===")
    all_ok = True
    for service, status in results.items():
        print(f"{service}: {'✅ OK' if status else '❌ FAIL'}")
        if not status:
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    # Check if specific test was requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "order":
            order_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            test_order_service(order_id)
        elif test_name == "health":
            service = sys.argv[2] if len(sys.argv) > 2 else "processing-order"
            port = int(sys.argv[3]) if len(sys.argv) > 3 else 5400
            check_service_health(service, port)
        elif test_name == "direct":
            order_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            test_process_order_direct(order_id)
    else:
        # Run all tests
        print("=== RUNNING SERVICE DIAGNOSTICS ===")
        test_process_order_direct() 