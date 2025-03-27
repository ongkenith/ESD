import requests
import json
import sys

def send_test_email(recipient_email=None):
    # Use the exact same values that worked in mailersend_api.py
    to_email = recipient_email or "shaunwang16@gmail.com"
    to_name = "Shaun Wang"
    from_email = "MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net"
    from_name = "Drone Delivery Service"
    subject = "Test Email: Direct MailerSend API"
    
    # MailerSend API key - using the exact same key that worked before
    api_key = "mlsn.6bdfb137652a12742bf620598b7374f59e91fb2f64b88e42636680365ffb92fc"
    
    # Simple HTML content
    html_content = """
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
            <h2 style="color: #333;">Test Email from Direct MailerSend API</h2>
            <p style="font-size: 16px; line-height: 1.5;">This is a test email sent directly using the MailerSend API.</p>
            <p style="font-size: 16px; line-height: 1.5;">If you received this, it confirms that your MailerSend account is working correctly.</p>
            <p style="font-size: 14px; color: #666; margin-top: 30px;">Thank you!</p>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = """
    Test Email from Direct MailerSend API
    
    This is a test email sent directly using the MailerSend API.
    
    If you received this, it confirms that your MailerSend account is working correctly.
    
    Thank you!
    """
    
    print(f"Sending test email to: {to_email}")
    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    # MailerSend API endpoint
    url = "https://api.mailersend.com/v1/email"
    
    # Prepare the headers
    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare the payload
    payload = {
        "from": {
            "email": from_email,
            "name": from_name
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
    
    # Convert payload to JSON
    json_payload = json.dumps(payload)
    
    try:
        # Send the request
        print(f"Sending request to {url}...")
        response = requests.post(url, headers=headers, data=json_payload)
        
        # Check response
        if response.status_code == 202:
            print(f"✅ Success! Email sent to {to_email}")
            print(f"Response code: {response.status_code}")
            return True
        else:
            print(f"❌ Failed to send email. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    send_test_email(recipient) 