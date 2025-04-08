import requests
import json
import pika
import time

# Define the notification data
notification_data = {
    "customer_id": 1,
    "message": "Your order #1 has been scheduled for delivery. A drone is on the way!",
    "order_id": 1
}

# Test 1: Direct HTTP API
print("\n--- TEST 1: Direct HTTP API ---")
try:
    response = requests.post(
        "http://localhost:5300/notify",
        json=notification_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Direct HTTP API test PASSED")
    else:
        print("❌ Direct HTTP API test FAILED")
except Exception as e:
    print(f"❌ Direct HTTP API test FAILED: {str(e)}")

# Test 2: RabbitMQ Queue
print("\n--- TEST 2: RabbitMQ Queue ---")

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

try:
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
    
    print(f"Sent message to RabbitMQ queue: {notification_data}")
    connection.close()
    print("✅ RabbitMQ Queue test PASSED")
    
    # Wait for notification service to process the message
    print("Waiting 5 seconds for the notification service to process the message...")
    time.sleep(5)
    
except Exception as e:
    print(f"❌ RabbitMQ Queue test FAILED: {str(e)}")

print("\nTesting completed!")
print("Check the notification service logs to see if the messages were received and processed correctly.") 