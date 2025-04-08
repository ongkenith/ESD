from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
import json
import pika
import threading
import time
import smtplib
import ssl
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# RabbitMQ connection settings
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', 'notification_queue')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')

# Email settings
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'true').lower() == 'true'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.mailersend.net')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', 'MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'mssp.c15zPmM.3zxk54vnek6ljy6v.175bFNr')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net')
EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', 'Drone Delivery Service')

# MailerSend API key (if using API instead of SMTP)
MAILERSEND_API_KEY = os.environ.get('MAILERSEND_API_KEY', 'mlsn.6bdfb137652a12742bf620598b7374f59e91fb2f64b88e42636680365ffb92fc')
USE_MAILERSEND_API = os.environ.get('USE_MAILERSEND_API', 'false').lower() == 'true'

# Function to simulate sending SMS
def send_sms(phone_number, message):
    print(f"Simulating SMS sent to {phone_number}: {message}")
    # In a real implementation, you would integrate with an SMS provider like Twilio
    return True

# Function to send an email using SMTP
def send_email_smtp(to_email, subject, message):
    try:
        if not EMAIL_ENABLED:
            print(f"Email is disabled. Would have sent to {to_email}")
            return True
            
        print(f"Sending email via SMTP to {to_email}")
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Create the HTML content
        html_content = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
                <h2 style="color: #333;">Drone Delivery Notification</h2>
                <p style="font-size: 16px; line-height: 1.5;">{message}</p>
                <p style="font-size: 14px; color: #666; margin-top: 30px;">Thank you for using our drone delivery service!</p>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999;">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>© 2023 Drone Delivery Service</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        Drone Delivery Notification

        {message}

        Thank you for using our drone delivery service!
        
        This is an automated message. Please do not reply to this email.
        """
        
        # Attach parts
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect to SMTP server
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
            
        print(f"Email successfully sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email via SMTP: {str(e)}")
        return False

# Function to send an email using MailerSend API
def send_email_api(to_email, subject, message, to_name="Customer"):
    try:
        if not EMAIL_ENABLED:
            print(f"Email is disabled. Would have sent to {to_email}")
            return True
            
        print(f"Sending email via MailerSend API to {to_email}")
        print(f"Using API key: {MAILERSEND_API_KEY}")
        print(f"From email: {EMAIL_FROM}")
        
        # MailerSend API endpoint
        url = "https://api.mailersend.com/v1/email"
        
        # Prepare the headers
        headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": f"Bearer {MAILERSEND_API_KEY}"
        }
        
        # Create the HTML content
        html_content = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
                <h2 style="color: #333;">Drone Delivery Notification</h2>
                <p style="font-size: 16px; line-height: 1.5;">{message}</p>
                <p style="font-size: 14px; color: #666; margin-top: 30px;">Thank you for using our drone delivery service!</p>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999;">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>© 2023 Drone Delivery Service</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        Drone Delivery Notification

        {message}

        Thank you for using our drone delivery service!
        
        This is an automated message. Please do not reply to this email.
        """
        
        # Prepare the payload
        payload = {
            "from": {
                "email": EMAIL_FROM,
                "name": EMAIL_FROM_NAME
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject,
            "text": text_content,
            "html": html_content
        }
        
        print(f"Request payload: {json.dumps(payload, indent=2)}")
        
        # Send the request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check response
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 202:
            print(f"Email successfully sent to {to_email} via API")
            return True
        else:
            print(f"Failed to send email via API. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Failed to send email via API: {str(e)}")
        print(f"Exception type: {type(e)}")
        print(f"Exception details: {str(e)}")
        return False

# Function to send an email (delegating to SMTP or API method)
def send_email(to_email, subject, message, to_name="Customer"):
    if USE_MAILERSEND_API:
        return send_email_api(to_email, subject, message, to_name)
    else:
        return send_email_smtp(to_email, subject, message)

# Function to get customer contact info
def get_customer_contact(customer_id):
    # Get customer details from customer service
    CUSTOMER_SERVICE_URL = os.environ.get('CUSTOMER_URL', 'http://customer:5001')
    customer_url = f"{CUSTOMER_SERVICE_URL}/customer/{customer_id}"
    
    try:
        # Call customer service API
        response = requests.get(customer_url)
        response.raise_for_status()  # Raise exception for bad status codes
        customer_data = response.json()
        
        # Map the response to our expected format
        return {
            "name": customer_data.get("Name", "Customer"),
            "phone": customer_data.get("Mobile_No", "00000000"),
            "email": customer_data.get("Email", "unknown@email.com")
        }
    except requests.exceptions.RequestException as e:
        print(f"Failed to get customer details from service: {str(e)}")
        # Return a default response in case of failure
        return {"name": "Customer", "phone": "00000000", "email": "unknown@email.com"}
    except Exception as e:
        print(f"Unexpected error getting customer details: {str(e)}")
        return {"name": "Customer", "phone": "00000000", "email": "unknown@email.com"}

# Function to process messages from RabbitMQ
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"Received notification request: {data}")
        
        customer_id = data.get('customer_id')
        message = data.get('message')
        order_id = data.get('order_id')
        
        if not all([customer_id, message, order_id]):
            print("Missing required fields in notification request")
            return
        
        customer = get_customer_contact(customer_id)
        phone_number = customer.get('phone')
        email = customer.get('email')
        name = customer.get('name')
        
        notification_results = {"sms": False, "email": False}
        
        # Send the SMS
        if phone_number:
            notification_results["sms"] = send_sms(phone_number, message)
            
        # Send the email
        if email:
            subject = f"Order #{order_id} Status Update"
            notification_results["email"] = send_email(email, subject, message, name)
        
        if notification_results["sms"] or notification_results["email"]:
            print(f"Successfully sent notification to customer {customer_id} about order {order_id}")
            print(f"Delivery methods: SMS: {notification_results['sms']}, Email: {notification_results['email']}")
        else:
            print(f"Failed to send notification to customer {customer_id}")
            
    except Exception as e:
        print(f"Error processing notification: {str(e)}")
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Function to start the AMQP consumer thread
def start_consumer():
    try:
        print(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}...")
        
        # Retry mechanism for connecting to RabbitMQ
        max_retries = 10
        retry_count = 0
        connected = False
        
        while not connected and retry_count < max_retries:
            try:
                # Use credentials (in case they're needed)
                credentials = pika.PlainCredentials('guest', 'guest')
                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_HOST, 
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=5
                )
                connection = pika.BlockingConnection(parameters)
                connected = True
                print(f"Successfully connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            except pika.exceptions.AMQPConnectionError as e:
                retry_count += 1
                wait_time = 5
                print(f"Failed to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}. Retry {retry_count}/{max_retries} in {wait_time} seconds...")
                print(f"Error details: {str(e)}")
                time.sleep(wait_time)
            except Exception as e:
                retry_count += 1
                wait_time = 5
                print(f"Unexpected error connecting to RabbitMQ: {str(e)}. Retry {retry_count}/{max_retries} in {wait_time} seconds...")
                time.sleep(wait_time)
        
        if not connected:
            raise Exception(f"Could not connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} after maximum retries")
        
        channel = connection.channel()
        
        # Declare the queue
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        
        # Set up the consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
        
        print(f" [*] Waiting for messages on queue '{RABBITMQ_QUEUE}'. To exit press CTRL+C")
        channel.start_consuming()
        
    except Exception as e:
        print(f"Consumer thread error: {str(e)}")
        print("Will attempt to reconnect in 30 seconds...")
        time.sleep(30)
        # Try to restart the consumer
        start_consumer()

# REST API endpoint for direct notifications (can be used for testing)
@app.route("/notify", methods=['POST'])
def notify():
    if request.is_json:
        try:
            data = request.get_json()
            print("\nReceived a direct notification request:", data)
            
            customer_id = data.get('customer_id')
            message = data.get('message')
            order_id = data.get('order_id')
            
            if not all([customer_id, message, order_id]):
                return jsonify({
                    "code": 400,
                    "message": "Missing required fields (customer_id, message, order_id)"
                }), 400
                
            customer = get_customer_contact(customer_id)
            phone_number = customer.get('phone')
            email = customer.get('email')
            name = customer.get('name')
            
            if not phone_number and not email:
                return jsonify({
                    "code": 404,
                    "message": f"No contact information found for customer ID {customer_id}"
                }), 404
                
            notification_results = {"sms": False, "email": False}
            
            # Send the SMS
            if phone_number:
                notification_results["sms"] = send_sms(phone_number, message)
            
            # Send the email
            if email:
                subject = f"Order #{order_id} Status Update"
                notification_results["email"] = send_email(email, subject, message, name)
            
            if notification_results["sms"] or notification_results["email"]:
                return jsonify({
                    "code": 200,
                    "data": {
                        "customer_id": customer_id,
                        "customer_name": name,
                        "phone_number": phone_number,
                        "email": email,
                        "message": message,
                        "order_id": order_id,
                        "notification_sent": {
                            "sms": notification_results["sms"],
                            "email": notification_results["email"]
                        }
                    },
                    "message": "Notification sent successfully"
                }), 200
            else:
                return jsonify({
                    "code": 500,
                    "message": "Failed to send notification via any channel"
                }), 500
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            
            return jsonify({
                "code": 500,
                "message": "notification.py internal error: " + ex_str
            }), 500
    
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

# Health check endpoint
@app.route("/health", methods=['GET'])
def health_check():
    # Return basic health info
    return jsonify({
        "status": "ok",
        "service": "notification-service",
        "email_enabled": EMAIL_ENABLED,
        "rabbitmq_host": RABBITMQ_HOST,
        "rabbitmq_queue": RABBITMQ_QUEUE,
        "use_mailersend_api": USE_MAILERSEND_API
    }), 200

# Test endpoint for directly testing email sending
@app.route("/test-email", methods=['GET'])
def test_email():
    try:
        to_email = request.args.get('email', 'shaunwang16@gmail.com')
        subject = "Test Email from Drone Delivery Service"
        message = "This is a test email from the Drone Delivery Service notification system."
        
        result = send_email(to_email, subject, message, "Test User")
        
        if result:
            return jsonify({
                "code": 200,
                "message": f"Test email sent successfully to {to_email}"
            }), 200
        else:
            return jsonify({
                "code": 500,
                "message": f"Failed to send test email to {to_email}"
            }), 500
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"Error sending test email: {str(e)}"
        }), 500

# Function to send message to RabbitMQ
@app.route("/notify-payment-success", methods=['GET'])
def send_to_rabbitmq():
    try:            
        message_data = f"""
Your payment was successful

Our drone is on the way to pick up your items. You will receive another notification when your order has reached its way to your location.

Thank you for choosing our Drone Delivery Service!
                """
        print("Attempting to connect to RabbitMQ...")
        
        # Retry mechanism for connecting to RabbitMQ
        max_retries = 5
        retry_count = 0
        connected = False
        
        while not connected and retry_count < max_retries:
            try:
                # Connect to RabbitMQ with credentials
                credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_HOST, 
                    port=RABBITMQ_PORT,
                    credentials=credentials
                )
                connection = pika.BlockingConnection(parameters)
                connected = True
            except pika.exceptions.AMQPConnectionError as e:
                retry_count += 1
                wait_time = 5
                print(f"Failed to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}. Retry {retry_count}/{max_retries} in {wait_time} seconds...")
                print(f"Error: {e}")
                time.sleep(wait_time)
        
        if not connected:
            raise Exception(f"Could not connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} after maximum retries")
        
        print(f"Successfully connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
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

# Start the consumer thread
if __name__ != '__main__':
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()

if __name__ == "__main__":
    # For running the Flask app directly
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5300) 