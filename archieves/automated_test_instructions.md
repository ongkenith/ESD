# Testing the Email Notification Functionality in the Drone Delivery System

This guide will help you test the email notification functionality that we've integrated into the Drone Delivery System. The system now sends two types of notifications:

1. **"In Transit" notification** - Sent when an order is processed and scheduled for delivery
2. **"Delivered" notification** - Sent when an order is marked as delivered

## Prerequisites

1. Docker must be installed and running on your system
2. Ensure you have Python 3 installed
3. The necessary Python packages: `requests`

## Step 1: Start the Services

Start all services using Docker Compose:

```bash
docker compose -f docker-compose_mac.yml up -d
```

Wait for all services to start properly (this may take a minute or so).

## Step 2: Verify the Notification Service

Run the direct email test to check if the notification service is working:

```bash
python test_email_notification.py
```

If successful, you should receive a test email at the specified address.

## Step 3: Test the Full Order Notification Flow

Run the full order notification flow test to verify both "In Transit" and "Delivered" notifications:

```bash
python test_order_notifications.py
```

This script will:
1. Process an order, triggering the "In Transit" email notification
2. Wait 30 seconds to simulate delivery time
3. Mark the order as delivered, triggering the "Delivered" email notification

## Expected Results

You should receive two distinct email notifications:

1. **First Email**: Order scheduled for delivery notification
   - Contains order ID
   - Status: IN TRANSIT
   - Pickup location
   - Drone ID
   - Estimated delivery time

2. **Second Email**: Order delivered notification
   - Contains order ID
   - Status: DELIVERED
   - Thank you message
   - Feedback request

## Troubleshooting

If you don't receive the emails:

1. Check that the notification service is running:
   ```bash
   docker logs esd-main-notification-1
   ```

2. Verify the email configuration in `docker-compose_mac.yml`:
   - `EMAIL_ENABLED` is set to "true"
   - MailerSend credentials are correct

3. Try testing with the direct API:
   ```bash
   curl "http://localhost:5300/test-email?email=your-email@example.com"
   ```

4. Check if RabbitMQ is running and accepting connections:
   ```bash
   docker logs esd-main-rabbitmq-1
   ```

## Manual Testing (Alternative)

You can also test the system manually:

1. Process an order:
   ```bash
   curl -X POST http://localhost:5400/process_order \
     -H "Content-Type: application/json" \
     -d '{"order_id": 1}'
   ```

2. After a while, mark the order as delivered:
   ```bash
   curl -X POST http://localhost:5400/order_delivered \
     -H "Content-Type: application/json" \
     -d '{"order_id": 1}'
   ```

Check your email inbox after each step to verify that you received the notifications. 