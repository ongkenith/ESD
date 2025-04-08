#!/usr/bin/env python3
import requests
import json
import pika
import time
import sys
import os

# Configuration
TEST_EMAIL = "shaunwang16@gmail.com"
NOTIFICATION_HOST = "notification:5300"  # Container name in docker compose
RABBITMQ_HOST = 'rabbitmq'  # Container name in docker compose
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

# Check if we're running in Docker or local mode
DOCKER_MODE = os.environ.get('DOCKER_MODE', 'false').lower() == 'true'
if not DOCKER_MODE:
    print("Running in local mode, using localhost for connections")
    NOTIFICATION_HOST = "localhost:5300"
    RABBITMQ_HOST = 'localhost'

def print_header(message):
    print("\n" + "="*70)
    print(message)
    print("="*70)

def send_notification_via_rabbitmq(customer_id, order_id, message):
    """Send a notification message through RabbitMQ"""
    print_header(f"SENDING NOTIFICATION VIA RABBITMQ: Order #{order_id}")
    
    # Create notification data
    notification_data = {
        "customer_id": customer_id,
        "message": message,
        "order_id": order_id
    }
    
    print(f"Notification data: {notification_data}")
    print(f"RabbitMQ Host: {RABBITMQ_HOST}")
    
    try:
        # Connect to RabbitMQ
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
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
        
        print(f"✅ Message sent to RabbitMQ queue")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Failed to send message to RabbitMQ: {str(e)}")
        return False

def simulate_order_flow():
    """Simulate the full order flow with notifications"""
    print_header("SIMULATING FULL ORDER FLOW")
    
    # Order details
    customer_id = 1  # Will use the email from get_customer_contact
    order_id = int(time.time()) % 10000  # Generate a random-ish order ID
    
    # Step 1: Order scheduled for delivery notification
    print("\n[Step 1] Sending 'Order Scheduled' notification...")
    scheduled_message = f"""
Your order #{order_id} has been scheduled for delivery!

Order Details:
- Pickup: Downtown Store
- Drone ID: DRN-{order_id}
- Status: IN TRANSIT

Our drone is on the way to pick up your items. You will receive another notification when your order is on its way to your location.

Thank you for choosing our Drone Delivery Service!
    """
    
    if not send_notification_via_rabbitmq(customer_id, order_id, scheduled_message.strip()):
        return False
    
    # Wait for notification to be processed
    print("\nWaiting 5 seconds for the notification to be processed...")
    for i in range(5, 0, -1):
        sys.stdout.write(f"\rWaiting... {i} seconds remaining ")
        sys.stdout.flush()
        time.sleep(1)
    print("\nContinuing...")
    
    # Step 2: Wait 30 seconds to simulate delivery time
    print("\n[Step 2] Waiting 30 seconds to simulate delivery time...")
    print("In a real system, this would be the time it takes for the drone to deliver the order.")
    for i in range(30, 0, -1):
        sys.stdout.write(f"\rDelivering order... {i} seconds remaining ")
        sys.stdout.flush()
        time.sleep(1)
    print("\nDelivery complete!")
    
    # Step 3: Order delivered notification
    print("\n[Step 3] Sending 'Order Delivered' notification...")
    delivered_message = f"""
Great news! Your order #{order_id} has been delivered!

Thank you for choosing our Drone Delivery Service. We hope you enjoy your items.

If you have any feedback about our service, please let us know.
    """
    
    return send_notification_via_rabbitmq(customer_id, order_id, delivered_message.strip())

if __name__ == "__main__":
    print_header("NOTIFICATION SYSTEM INTEGRATION TEST")
    print(f"Test email: {TEST_EMAIL}")
    print(f"RabbitMQ Host: {RABBITMQ_HOST}")
    print(f"Notification Service: {NOTIFICATION_HOST}")
    
    # Ask if user wants to run the simulation
    print("\nDo you want to run the order notification flow simulation? (y/n)")
    choice = input("> ")
    
    if choice.lower() == 'y':
        # Run the full order flow
        if simulate_order_flow():
            print("\n✅ Order notification flow simulation completed successfully!")
            print("You should receive two emails at", TEST_EMAIL)
            print("1. Order scheduled for delivery notification")
            print("2. Order delivered notification")
        else:
            print("\n❌ Order notification flow simulation failed.")
    else:
        print("Skipping simulation.")
    
    print("\nTest script completed.") 