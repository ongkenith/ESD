#!/usr/bin/env python3
import requests
import json
import sys

# Define the service URL
NOTIFICATION_HOST = "localhost:5300"
test_email_url = f"http://{NOTIFICATION_HOST}/test-email"

# Email to send the test notification to
TEST_EMAIL = "shaunwang16@gmail.com"

def test_direct_email_notification():
    """
    Test the email notification functionality directly by calling the 
    notification service's test-email endpoint.
    """
    print("="*70)
    print("DIRECT EMAIL NOTIFICATION TEST")
    print("="*70)
    
    print(f"Sending test email to: {TEST_EMAIL}")
    
    try:
        # Construct the URL with the email parameter
        url = f"{test_email_url}?email={TEST_EMAIL}"
        print(f"Request URL: {url}")
        
        # Send GET request to the test-email endpoint
        response = requests.get(url, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Test email sent successfully!")
            print(f"Response: {result.get('message', 'No message provided')}")
            return True
        else:
            print(f"\n❌ Failed to send test email. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running direct email notification test...")
    
    if test_direct_email_notification():
        print("\n✅ TEST COMPLETED SUCCESSFULLY!")
        print(f"A test email should have been sent to {TEST_EMAIL}.")
        print("Please check your inbox to confirm receipt.")
    else:
        print("\n❌ TEST FAILED!")
        print("Please check the error messages above and ensure the notification service is running.") 