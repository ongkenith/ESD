import requests
import json
import pika
import sys
import os
import time

# Check if running in Docker mode
DOCKER_MODE = os.environ.get('DOCKER_MODE', 'false').lower() == 'true'

# Set the notification service URL based on environment
if DOCKER_MODE:
    NOTIFICATION_URL = "http://notification:5300/notify"
    RABBITMQ_HOST = 'rabbitmq'
else:
    NOTIFICATION_URL = "http://localhost:5300/notify"
    RABBITMQ_HOST = 'localhost'

# RabbitMQ configuration
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

def test_notification_api(customer_id=1, order_id=1, message=None):
    """Test the direct notification API endpoint"""
    print(f"\n=== TESTING NOTIFICATION API ===")
    print(f"URL: {NOTIFICATION_URL}")
    
    if message is None:
        message = f"Your order #{order_id} has been scheduled for delivery. A drone is on the way!"
    
    # Create notification data
    notification_data = {
        "customer_id": customer_id,
        "message": message,
        "order_id": order_id
    }
    
    print(f"Sending notification with data: {notification_data}")
    
    try:
        # Send notification via direct API
        response = requests.post(
            NOTIFICATION_URL,
            json=notification_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Process the response
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            
            if response.status_code == 200:
                print("\n✅ NOTIFICATION API TEST SUCCESSFUL")
                return True
            else:
                print("\n❌ NOTIFICATION API TEST FAILED")
                if response_json.get("message"):
                    print(f"Reason: {response_json.get('message')}")
                return False
        except ValueError:
            print(response.text)
            print("\n❌ NOTIFICATION API TEST FAILED: Could not parse JSON response")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_notification_queue(customer_id=1, order_id=1, message=None):
    """Test sending a notification through RabbitMQ queue"""
    print(f"\n=== TESTING NOTIFICATION QUEUE ===")
    print(f"RabbitMQ Host: {RABBITMQ_HOST}")
    print(f"RabbitMQ Queue: {RABBITMQ_QUEUE}")
    
    if message is None:
        message = f"Your order #{order_id} has been scheduled for delivery. A drone is on the way!"
    
    # Create notification data
    notification_data = {
        "customer_id": customer_id,
        "message": message,
        "order_id": order_id
    }
    
    print(f"Sending notification with data: {notification_data}")
    
    try:
        print("Attempting to connect to RabbitMQ...")
        
        # Connect to RabbitMQ
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
            body=json.dumps(notification_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        
        print(f" [x] Sent notification message to queue: {notification_data}")
        connection.close()
        
        print("\n✅ NOTIFICATION QUEUE TEST SUCCESSFUL")
        print("The notification service should now process this message.")
        print("Check the notification service logs to see if the message was received and processed.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Could not send message to RabbitMQ: {str(e)}")
        return False

if __name__ == "__main__":
    # Process command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--docker':
        os.environ['DOCKER_MODE'] = 'true'
        print("Docker mode enabled via command line")
    
    # Parse test arguments
    test_api = True
    test_queue = True
    customer_id = 1
    order_id = 1
    custom_message = None
    
    for i, arg in enumerate(sys.argv):
        if arg == '--api-only':
            test_queue = False
        elif arg == '--queue-only':
            test_api = False
        elif arg == '--customer' and i+1 < len(sys.argv):
            try:
                customer_id = int(sys.argv[i+1])
            except ValueError:
                print(f"Invalid customer ID: {sys.argv[i+1]}")
        elif arg == '--order' and i+1 < len(sys.argv):
            try:
                order_id = int(sys.argv[i+1])
            except ValueError:
                print(f"Invalid order ID: {sys.argv[i+1]}")
        elif arg == '--message' and i+1 < len(sys.argv):
            custom_message = sys.argv[i+1]
    
    # Run the tests
    api_success = True
    queue_success = True
    
    if test_api:
        api_success = test_notification_api(
            customer_id=customer_id,
            order_id=order_id,
            message=custom_message
        )
    
    if test_queue:
        queue_success = test_notification_queue(
            customer_id=customer_id,
            order_id=order_id,
            message=custom_message
        )
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    if test_api:
        print(f"API Test: {'✅ PASSED' if api_success else '❌ FAILED'}")
    if test_queue:
        print(f"Queue Test: {'✅ PASSED' if queue_success else '❌ FAILED'}")
    
    if (test_api and not api_success) or (test_queue and not queue_success):
        sys.exit(1)  # Exit with error code if any test failed 