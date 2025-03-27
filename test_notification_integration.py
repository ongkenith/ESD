#!/usr/bin/env python3
import requests
import json
import pika
import time
import sys

# Configuration
TEST_EMAIL = "shaunwang16@gmail.com"
NOTIFICATION_HOST = "localhost:5300"
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

def print_header(message):
    print("\n" + "="*70)
    print(message)
    print("="*70)

def test_rabbitmq_connection():
    """Test connection to RabbitMQ"""
    print_header("TESTING RABBITMQ CONNECTION")
    
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
        
        # Verify the connection
        print("✅ Successfully connected to RabbitMQ")
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to RabbitMQ: {str(e)}")
        return False

def test_notification_service():
    """Test direct connection to notification service"""
    print_header("TESTING NOTIFICATION SERVICE API")
    
    health_url = f"http://{NOTIFICATION_HOST}/health"
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ Notification service is running")
            return True
        else:
            print(f"❌ Notification service returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to notification service: {str(e)}")
        return False

def test_direct_email():
    """Test direct email sending through the API"""
    print_header("TESTING DIRECT EMAIL API")
    
    test_email_url = f"http://{NOTIFICATION_HOST}/test-email?email={TEST_EMAIL}"
    try:
        response = requests.get(test_email_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test email sent successfully")
            print(f"Response: {result}")
            return True
        else:
            print(f"❌ Failed to send test email. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")
        return False

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
    customer_id = 1  # Will use shaunwang16@gmail.com from get_customer_contact
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
    print("\nWaiting 10 seconds for the notification to be processed...")
    for i in range(10, 0, -1):
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
    
    # Test 1: RabbitMQ Connection
    if not test_rabbitmq_connection():
        print("\n❌ RabbitMQ connection test failed. Please check if RabbitMQ is running.")
        sys.exit(1)
    
    # Test 2: Notification Service API
    if not test_notification_service():
        print("\n❌ Notification service test failed. Please check if the service is running.")
        sys.exit(1)
    
    # Test 3: Direct Email API
    if not test_direct_email():
        print("\n❌ Direct email test failed. Email functionality may not be working.")
        print("Continuing with RabbitMQ tests anyway...")
    
    # Ask if user wants to run the full simulation
    print("\nDo you want to run the full order notification flow simulation? (y/n)")
    choice = input("> ")
    
    if choice.lower() == 'y':
        # Test 4: Full Order Flow
        if simulate_order_flow():
            print("\n✅ Order notification flow simulation completed successfully!")
            print("You should receive two emails:")
            print("1. Order scheduled for delivery notification")
            print("2. Order delivered notification")
        else:
            print("\n❌ Order notification flow simulation failed.")
    else:
        print("Skipping full order flow simulation.")
    
    print("\nTest script completed. Check your email inbox for notifications.") 