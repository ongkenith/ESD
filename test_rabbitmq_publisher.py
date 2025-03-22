import pika
import json
import time

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'  # Use localhost since we're accessing from host
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
    # Test message
    notification_data = {
        "customer_id": 1,
        "message": "This is a test notification message from our publisher script!",
        "order_id": 1
    }
    
    # Send the notification
    result = send_to_rabbitmq(notification_data)
    
    if result:
        print("Successfully sent notification to RabbitMQ!")
    else:
        print("Failed to send notification to RabbitMQ.") 