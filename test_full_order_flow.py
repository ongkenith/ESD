import requests
import json
import pika
import time
import random
import os
import sys

# Check if running in Docker mode
DOCKER_MODE = os.environ.get('DOCKER_MODE', 'false').lower() == 'true'

# Define URLs with conditional hosts based on environment
if DOCKER_MODE:
    print("Running in Docker mode with container hostnames")
    # Docker container hostnames
    ORDER_HOST = "order:5010"
    STORE_HOST = "store:5003"
    CONDITION_CHECK_HOST = "condition-check:5100"
    NOTIFICATION_HOST = "notification:5300"
    RABBITMQ_HOST = 'rabbitmq'
else:
    print("Running in local mode with localhost")
    # Local development (localhost)
    ORDER_HOST = "localhost:5010"
    STORE_HOST = "localhost:5003" 
    CONDITION_CHECK_HOST = "localhost:5100"
    NOTIFICATION_HOST = "localhost:5300"
    RABBITMQ_HOST = 'localhost'

# Service URLs
ORDER_URL = f"http://{ORDER_HOST}/order"
STORE_URL = f"http://{STORE_HOST}/store"
CONDITION_CHECK_URL = f"http://{CONDITION_CHECK_HOST}/check-condition"
NOTIFICATION_URL = f"http://{NOTIFICATION_HOST}/notify"

# RabbitMQ configuration
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

def send_to_rabbitmq(message_data):
    """Send a notification message to RabbitMQ"""
    try:
        print("Attempting to connect to RabbitMQ...")
        
        # Connect to RabbitMQ with credentials
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST, 
            port=RABBITMQ_PORT,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        
        print("Successfully connected to RabbitMQ")
        channel = connection.channel()
        
        # Declare the queue
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        
        # Send the message
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(message_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        
        print(f" [x] Sent notification message to queue: {message_data}")
        connection.close()
        return True
        
    except Exception as e:
        print(f"Failed to send message to RabbitMQ: {str(e)}")
        return False

def simulate_weather_check(pickup_location, delivery_location):
    """Simulate checking weather conditions"""
    print("\n--- STEP 1: Checking Weather Conditions ---")
    
    try:
        weather_data = {
            "pickUpLocation": pickup_location,
            "deliveryLocation": delivery_location
        }
        
        print(f"Sending request to check weather conditions: {weather_data}")
        response = requests.post(
            CONDITION_CHECK_URL,
            json=weather_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Weather check result: {result}")
            print("✅ Weather conditions are suitable for drone flight")
            return True
        else:
            print(f"❌ Weather conditions are NOT suitable for drone flight: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Weather check failed: {str(e)}")
        return False

def simulate_order_processing(order_id, store_id, pickup_location, delivery_location):
    """Simulate processing an order"""
    print("\n--- STEP 2: Processing Order ---")
    
    # Step 1: Update order status to PENDING
    print("Updating order status to PENDING...")
    # This would typically be done through the Order service
    
    # Step 2: Find available drone
    print("Finding available drone...")
    # This would typically be done through the Drone service
    drone_id = random.randint(1, 5)  # Simulate finding a drone
    
    # Step 3: Schedule delivery with drone
    schedule_data = {
        "drone_id": drone_id,
        "pickUpLocation": pickup_location,
        "deliveryLocation": delivery_location,
        "order_id": order_id,
        "storeId": store_id,
        "weatherCheck": True
    }
    
    print(f"Scheduling delivery with drone: {schedule_data}")
    # This would typically be done through the Scheduling service
    
    # Step 4: Update order status to SCHEDULED FOR DELIVERY
    print("Updating order status to SCHEDULED FOR DELIVERY...")
    # This would typically be done through the Order service
    
    return drone_id

def send_notification(customer_id, order_id):
    """Send notification to customer"""
    print("\n--- STEP 3: Sending Notification ---")
    
    # Create notification message
    notification_data = {
        "customer_id": customer_id,
        "message": f"Your order #{order_id} has been scheduled for delivery. A drone is on the way!",
        "order_id": order_id
    }
    
    # Send via RabbitMQ
    print("Sending notification via RabbitMQ...")
    rabbitmq_result = send_to_rabbitmq(notification_data)
    
    # Also test direct API for comparison
    print("Sending notification via direct API...")
    try:
        response = requests.post(
            NOTIFICATION_URL,
            json=notification_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Direct API Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Direct API Response: {response.json()}")
            print("✅ Direct notification API call successful")
            direct_api_success = True
        else:
            print(f"❌ Direct notification API call failed: {response.text}")
            direct_api_success = False
    except Exception as e:
        print(f"❌ Direct notification API call failed: {str(e)}")
        direct_api_success = False
    
    return rabbitmq_result, direct_api_success

if __name__ == "__main__":
    print("\n=== SIMULATING COMPLETE ORDER FLOW ===\n")
    
    # Process command line argument for Docker mode
    if len(sys.argv) > 1 and sys.argv[1] == '--docker':
        os.environ['DOCKER_MODE'] = 'true'
        print("Docker mode enabled via command line")
    
    print(f"Using RabbitMQ host: {RABBITMQ_HOST}")
    print(f"Using Condition Check URL: {CONDITION_CHECK_URL}")
    print(f"Using Notification URL: {NOTIFICATION_URL}")
    
    # Order details (simulated)
    order_id = 1
    customer_id = 1
    store_id = 1
    pickup_location = 1  # Store ID
    delivery_location = 1  # Order ID
    
    # Step 1: Check weather conditions
    weather_ok = simulate_weather_check(pickup_location, delivery_location)
    
    if weather_ok:
        # Step 2: Process order
        drone_id = simulate_order_processing(order_id, store_id, pickup_location, delivery_location)
        
        # Step 3: Send notification
        rabbitmq_success, api_success = send_notification(customer_id, order_id)
        
        # Summary
        print("\n=== SIMULATION SUMMARY ===")
        print(f"Order ID: {order_id}")
        print(f"Customer ID: {customer_id}")
        print(f"Store ID: {store_id}")
        print(f"Assigned Drone ID: {drone_id}")
        print(f"Weather Check: {'✅ Passed' if weather_ok else '❌ Failed'}")
        print(f"RabbitMQ Notification: {'✅ Sent' if rabbitmq_success else '❌ Failed'}")
        print(f"Direct API Notification: {'✅ Sent' if api_success else '❌ Failed'}")
        
        if weather_ok and rabbitmq_success and api_success:
            print("\n✅ SIMULATION COMPLETED SUCCESSFULLY")
        else:
            print("\n⚠️ SIMULATION COMPLETED WITH SOME ISSUES")
    else:
        print("\n❌ SIMULATION STOPPED: Weather conditions not suitable for drone flight") 