#!/usr/bin/env python3
import requests
import json
import time
import sys

# Define the service URLs
PROCESSING_ORDER_HOST = "localhost:5400"
processing_order_url = f"http://{PROCESSING_ORDER_HOST}/process_order"
order_delivered_url = f"http://{PROCESSING_ORDER_HOST}/order_delivered"

# Use a specific test email address
TEST_EMAIL = "shaunwang16@gmail.com"

def test_full_order_notification_flow():
    """
    Test the full order notification flow:
    1. Process an order (triggers 'in transit' notification)
    2. Wait 30 seconds 
    3. Mark the order as delivered (triggers 'delivered' notification)
    """
    print("="*70)
    print("DRONE DELIVERY NOTIFICATION FLOW TEST")
    print("="*70)
    print(f"Test email: {TEST_EMAIL}")
    print("="*70)
    
    # Step 1: Process an order (this will trigger the first notification)
    print("\n[Step 1] Processing order (will trigger 'In Transit' notification)...")
    
    # Order data
    order_data = {
        "order_id": 1  # Using a known order ID from the database
    }
    
    try:
        # Send request to process the order
        print(f"Sending request to {processing_order_url}...")
        response = requests.post(
            processing_order_url,
            json=order_data,
            timeout=10  # Add timeout
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Order processed successfully!")
            print(f"Order ID: {order_data['order_id']}")
            print(f"Message: {result.get('message', 'No message provided')}")
            
            # Extract the order ID for the next step
            order_id = order_data['order_id']
        else:
            print(f"❌ Failed to process order. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error when processing order: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error when processing order: {str(e)}")
        return False
    
    print("\n✅ First notification (In Transit) should have been sent to your email.")
    print(f"Please check {TEST_EMAIL} for the notification.")
    
    # Step 2: Wait for 30 seconds
    print(f"\n[Step 2] Waiting for 30 seconds before marking order as delivered...")
    print("This simulates the time it takes for the drone to deliver the order.")
    
    for i in range(30, 0, -1):
        sys.stdout.write(f"\rDelivering order... {i} seconds remaining ")
        sys.stdout.flush()
        time.sleep(1)
    
    print("\n\nDelivery complete!")
    
    # Step 3: Mark the order as delivered
    print("\n[Step 3] Marking order as delivered (will trigger 'Delivered' notification)...")
    
    # Prepare delivered data
    delivered_data = {
        "order_id": order_id
    }
    
    try:
        # Send request to mark order as delivered
        print(f"Sending request to {order_delivered_url}...")
        response = requests.post(
            order_delivered_url,
            json=delivered_data,
            timeout=10  # Add timeout
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Order marked as delivered successfully!")
            print(f"Order ID: {order_id}")
            print(f"Message: {result.get('message', 'No message provided')}")
            return True
        else:
            print(f"❌ Failed to mark order as delivered. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error when marking order as delivered: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error when marking order as delivered: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running full order notification flow test...")
    
    if test_full_order_notification_flow():
        print("\n✅ TEST COMPLETED SUCCESSFULLY!")
        print("You should have received two email notifications:")
        print("1. Order scheduled for delivery (In Transit)")
        print("2. Order delivered")
        print("\nCheck your email inbox to confirm.")
    else:
        print("\n❌ TEST FAILED!")
        print("Please check the error messages above.") 