import pika
import json
import sys

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'  # Use localhost since we're accessing from host
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'notification_queue'
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"\nReceived message: {data}")
        
        customer_id = data.get('customer_id')
        message = data.get('message')
        order_id = data.get('order_id')
        
        if all([customer_id, message, order_id]):
            print(f"Customer ID: {customer_id}")
            print(f"Order ID: {order_id}")
            print(f"Message: {message}")
            print(f"Would send SMS to customer {customer_id} about order {order_id}")
        else:
            print("Message is missing required fields")
            
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
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
        
        # Set up the consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
        
        print(f" [*] Waiting for messages on queue '{RABBITMQ_QUEUE}'. To exit press CTRL+C")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("Consumer stopped by user")
        if 'connection' in locals() and connection:
            connection.close()
        sys.exit(0)
    except Exception as e:
        print(f"Consumer error: {str(e)}")
        if 'connection' in locals() and connection:
            connection.close()
        sys.exit(1)

if __name__ == "__main__":
    start_consumer() 