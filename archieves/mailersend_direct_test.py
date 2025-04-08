#!/usr/bin/env python3
import requests
import json
import sys

# MailerSend API key
MAILERSEND_API_KEY = "mlsn.6bdfb137652a12742bf620598b7374f59e91fb2f64b88e42636680365ffb92fc"

# Email settings
FROM_EMAIL = "MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net"
FROM_NAME = "Drone Delivery Service"
TO_EMAIL = "shaunwang16@gmail.com"
TO_NAME = "Shaun Wang"

def send_email_via_mailersend(subject, html_content, text_content):
    """Send an email using the MailerSend API"""
    print(f"Sending email to {TO_EMAIL} via MailerSend API...")
    
    # MailerSend API endpoint
    url = "https://api.mailersend.com/v1/email"
    
    # Prepare the headers
    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {MAILERSEND_API_KEY}"
    }
    
    # Prepare the payload
    payload = {
        "from": {
            "email": FROM_EMAIL,
            "name": FROM_NAME
        },
        "to": [
            {
                "email": TO_EMAIL,
                "name": TO_NAME
            }
        ],
        "subject": subject,
        "text": text_content,
        "html": html_content
    }
    
    # Convert payload to JSON
    json_payload = json.dumps(payload)
    
    # Print request details for debugging
    print("\nRequest details:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json_payload}")
    
    try:
        # Send the request
        response = requests.post(url, headers=headers, data=json_payload)
        
        # Print response details
        print("\nResponse details:")
        print(f"Status code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        # Check response
        if response.status_code == 202:
            print("\n✅ Email sent successfully!")
            return True
        else:
            print(f"\n❌ Failed to send email. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error sending email: {str(e)}")
        return False

def main():
    # Create a test order
    order_id = 12345
    
    # Create email content
    subject = f"Drone Delivery Service - Order #{order_id} Status Update"
    
    # HTML content with nice formatting
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #333;">Drone Delivery Notification</h2>
            
            <p style="font-size: 16px; line-height: 1.5;">Your order #{order_id} has been scheduled for delivery!</p>
            
            <div style="background-color: #f9f9f9; border-left: 4px solid #4CAF50; padding: 15px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #4CAF50;">Order Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Order ID:</strong></td>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{order_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Status:</strong></td>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;">In Transit</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Pickup Location:</strong></td>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Downtown Store</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Drone ID:</strong></td>
                        <td style="padding: 8px 0; border-bottom: 1px solid #eee;">DRN-{order_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><strong>Estimated Delivery:</strong></td>
                        <td style="padding: 8px 0;">30 minutes</td>
                    </tr>
                </table>
            </div>
            
            <p style="font-size: 16px; line-height: 1.5;">Our drone is on the way to pick up your items. You will receive another notification when your order is delivered.</p>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">Thank you for choosing our Drone Delivery Service!</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999;">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>© 2023 Drone Delivery Service</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Drone Delivery Notification
    
    Your order #{order_id} has been scheduled for delivery!
    
    Order Details:
    - Order ID: {order_id}
    - Status: In Transit
    - Pickup Location: Downtown Store
    - Drone ID: DRN-{order_id}
    - Estimated Delivery: 30 minutes
    
    Our drone is on the way to pick up your items. You will receive another notification when your order is delivered.
    
    Thank you for choosing our Drone Delivery Service!
    
    This is an automated message. Please do not reply to this email.
    """
    
    # Send the email
    success = send_email_via_mailersend(subject, html_content, text_content)
    
    if success:
        print("Email test successful!")
        sys.exit(0)
    else:
        print("Email test failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 