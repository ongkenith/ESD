import pika
import json
import time

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

def send_to_rabbitmq(message_data):
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

if __name__ == "__main__":
    # Simulate processing an order and sending a notification
    print("\n--- Simulating Order Processing with Notification ---")
    
    # Order details (simulated from database)
    order_id = 1
    customer_id = 1
    
    # Create notification message
    notification_data = {
        "customer_id": customer_id,
        "message": f"Your order #{order_id} has been scheduled for delivery. A drone is on the way!",
        "order_id": order_id
    }
    
    # Send notification
    result = send_to_rabbitmq(notification_data)
    
    if result:
        print("✅ Successfully sent notification message to RabbitMQ!")
        print("The notification service should now process this message.")
        print("Check the notification service logs to see if the message was received and processed.")
    else:
        print("❌ Failed to send notification message to RabbitMQ.") 