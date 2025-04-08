import requests
import base64
import json

# RabbitMQ configuration
RABBITMQ_HOST = 'localhost'  # Use localhost since we're accessing from host
RABBITMQ_PORT = 15672  # Management API port
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'
RABBITMQ_QUEUE = 'notification_queue'

def get_rabbitmq_info():
    try:
        print(f"Attempting to connect to RabbitMQ Management API at {RABBITMQ_HOST}:{RABBITMQ_PORT}...")
        
        # Basic authentication credentials
        auth_string = f"{RABBITMQ_USER}:{RABBITMQ_PASS}"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        headers = {
            'Authorization': f'Basic {base64_auth}'
        }
        
        # Get overview info
        overview_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_PORT}/api/overview"
        overview_response = requests.get(overview_url, headers=headers)
        
        if overview_response.status_code == 200:
            print("Successfully connected to RabbitMQ Management API")
            overview_data = overview_response.json()
            print(f"RabbitMQ Version: {overview_data.get('rabbitmq_version')}")
            print(f"Erlang Version: {overview_data.get('erlang_version')}")
            print(f"Cluster Name: {overview_data.get('cluster_name')}")
            
            # Get queues info
            queues_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_PORT}/api/queues"
            queues_response = requests.get(queues_url, headers=headers)
            
            if queues_response.status_code == 200:
                queues_data = queues_response.json()
                print(f"\nFound {len(queues_data)} queues:")
                
                # Check if our queue exists
                queue_exists = False
                for queue in queues_data:
                    print(f"- {queue.get('name')} (messages: {queue.get('messages')})")
                    if queue.get('name') == RABBITMQ_QUEUE:
                        queue_exists = True
                
                if not queue_exists:
                    print(f"\nQueue '{RABBITMQ_QUEUE}' not found. Creating it...")
                    
                    # Create the queue if it doesn't exist
                    create_queue_url = f"http://{RABBITMQ_HOST}:{RABBITMQ_PORT}/api/queues/%2F/{RABBITMQ_QUEUE}"
                    create_queue_data = {
                        "auto_delete": False,
                        "durable": True,
                        "arguments": {}
                    }
                    create_response = requests.put(
                        create_queue_url, 
                        headers={**headers, 'Content-Type': 'application/json'}, 
                        data=json.dumps(create_queue_data)
                    )
                    
                    if create_response.status_code in [201, 204]:
                        print(f"Queue '{RABBITMQ_QUEUE}' created successfully")
                    else:
                        print(f"Failed to create queue. Status: {create_response.status_code}, Response: {create_response.text}")
                
                return True
            else:
                print(f"Failed to get queues info. Status: {queues_response.status_code}, Response: {queues_response.text}")
        else:
            print(f"Failed to connect to RabbitMQ Management API. Status: {overview_response.status_code}, Response: {overview_response.text}")
            
        return False
        
    except Exception as e:
        print(f"Error connecting to RabbitMQ Management API: {str(e)}")
        return False

if __name__ == "__main__":
    get_rabbitmq_info() 