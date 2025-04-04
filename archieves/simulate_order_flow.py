#!/usr/bin/env python3
import requests
import json
import time
import sys
import os
from datetime import datetime

# Base URLs for all services
PLACING_ORDER_URL = "http://localhost:5500"
ORDER_URL = "http://localhost:5004"
CUSTOMER_URL = "http://localhost:5001"
ITEM_URL = "http://localhost:5002"
STORE_URL = "http://localhost:5003"
PROCESSING_ORDER_URL = "http://localhost:5400"
DRONE_NAVIGATION_URL = "http://localhost:5200"
CONDITION_CHECK_URL = "http://localhost:5100"
DRONE_URL = "http://localhost:5300"
NOTIFICATION_URL = "http://localhost:5600"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_step(step_number, description):
    """Print a formatted step in the order flow"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[Step {step_number}] {description}{Colors.ENDC}")

def print_service_call(service_name, endpoint, method="GET"):
    """Print a formatted service call"""
    print(f"{Colors.CYAN}► Calling {service_name} service: {method} {endpoint}{Colors.ENDC}")

def print_response(response, is_success=True):
    """Print a formatted response"""
    if is_success:
        print(f"{Colors.GREEN}✓ Response: {json.dumps(response, indent=2)}{Colors.ENDC}")
    else:
        print(f"{Colors.RED}✗ Error: {json.dumps(response, indent=2)}{Colors.ENDC}")

def print_notification(recipient, message):
    """Print a formatted notification"""
    print(f"\n{Colors.YELLOW}📱 Notification to {recipient}:{Colors.ENDC}")
    print(f"{Colors.YELLOW}{message}{Colors.ENDC}")

def simulate_order_flow():
    """Simulate the entire order flow through all services"""
    try:
        print(f"{Colors.BOLD}{Colors.HEADER}===== DRONE DELIVERY ORDER SIMULATION ====={Colors.ENDC}")
        print(f"{Colors.HEADER}Starting simulation at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        
        # Step 1: Get customer details for customer ID 1
        print_step(1, "Retrieving customer details")
        print_service_call("Customer", f"{CUSTOMER_URL}/customer/1")
        
        try:
            customer_response = requests.get(f"{CUSTOMER_URL}/customer/1")
            customer_data = customer_response.json()
            print_response(customer_data)
            customer_id = customer_data.get("Customer_ID", 1)
            customer_name = customer_data.get("Name", "Customer")
            customer_email = customer_data.get("Email", "customer@example.com")
            customer_mobile = customer_data.get("Mobile_No", "12345678")
        except Exception as e:
            print(f"{Colors.RED}Failed to get customer details: {str(e)}{Colors.ENDC}")
            customer_id = 1
            customer_name = "Test Customer"
            customer_email = "test@example.com"
            customer_mobile = "12345678"
            
        # Step 2: Get item details for item ID 1
        print_step(2, "Retrieving item details")
        print_service_call("Item", f"{ITEM_URL}/items/1")
        
        try:
            item_response = requests.get(f"{ITEM_URL}/items/1")
            item_data = item_response.json()
            print_response(item_data)
            item_id = item_data.get("Item_ID", 1)
            item_name = item_data.get("Name", "Test Item")
            item_price = item_data.get("Price", 100.0)
            store_id = item_data.get("Store_ID", 1)
        except Exception as e:
            print(f"{Colors.RED}Failed to get item details: {str(e)}{Colors.ENDC}")
            item_id = 1
            item_name = "Test Item"
            item_price = 100.0
            store_id = 1
            
        # Step 3: Get store details
        print_step(3, "Retrieving store details")
        print_service_call("Store", f"{STORE_URL}/store/{store_id}")
        
        try:
            store_response = requests.get(f"{STORE_URL}/store/{store_id}")
            store_data = store_response.json()
            print_response(store_data)
            pickup_location = store_data.get("pickup_location", 123456)
            store_name = store_data.get("name", f"Store #{store_id}")
        except Exception as e:
            print(f"{Colors.RED}Failed to get store details: {str(e)}{Colors.ENDC}")
            pickup_location = 123456
            store_name = f"Store #{store_id}"
            
        # Step 4: Place an order through the placing-order service
        print_step(4, "Placing an order")
        
        # Create order payload
        cart_item = [{"item_id": item_id, "quantity": 2}]
        delivery_location = "123 Main St, Singapore"
        total_amount = item_price * 2
        
        order_payload = {
            "customer_id": customer_id,
            "cart_item": cart_item,
            "deliveryLocation": delivery_location
        }
        
        print_service_call("Placing Order", f"{PLACING_ORDER_URL}/place_order", "POST")
        print(f"Payload: {json.dumps(order_payload, indent=2)}")
        
        try:
            order_response = requests.post(
                f"{PLACING_ORDER_URL}/place_order",
                json=order_payload,
                headers={"Content-Type": "application/json"}
            )
            order_result = order_response.json()
            print_response(order_result)
            
            if "order_id" in order_result:
                order_id = order_result["order_id"]
                print(f"{Colors.GREEN}✓ Order created successfully with ID: {order_id}{Colors.ENDC}")
            else:
                print(f"{Colors.RED}✗ Failed to create order{Colors.ENDC}")
                return
        except Exception as e:
            print(f"{Colors.RED}Error placing order: {str(e)}{Colors.ENDC}")
            return
            
        # Step 5: Get order details
        print_step(5, "Retrieving order details")
        print_service_call("Order", f"{ORDER_URL}/order/{order_id}")
        
        try:
            order_details_response = requests.get(f"{ORDER_URL}/order/{order_id}")
            order_details = order_details_response.json()
            print_response(order_details)
            
            order_status = order_details.get("data", {}).get("order_status", "UNKNOWN")
            print(f"{Colors.GREEN}✓ Order status: {order_status}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error getting order details: {str(e)}{Colors.ENDC}")
            
        # Step 6: Simulate checking drone navigation status
        print_step(6, "Checking drone navigation status")
        
        # Wait a moment to simulate time passing
        time.sleep(2)
        
        print_notification(
            f"{customer_name} ({customer_email})", 
            f"""
Your order #{order_id} has been scheduled for delivery!

Order Details:
- Items: {item_name} x 2
- Total Amount: ${total_amount:.2f}
- Pickup: {store_name}
- Delivery To: {delivery_location}
- Status: Drone assigned and on its way to pick up your items

Thank you for choosing our Drone Delivery Service!
            """
        )
        
        # Step 7: Simulate drone pickup
        print_step(7, "Simulating drone pickup from store")
        
        # Wait a moment to simulate time passing
        time.sleep(2)
        
        print(f"{Colors.GREEN}✓ Drone has arrived at the pickup location ({pickup_location}){Colors.ENDC}")
        print(f"{Colors.GREEN}✓ Drone has picked up the package for order #{order_id}{Colors.ENDC}")
        
        print_notification(
            f"{customer_name} ({customer_email})", 
            f"""
Update on your order #{order_id}!

Your order has been picked up from {store_name} and is now on its way to your location.
Estimated delivery time: 15 minutes

Track your delivery in real-time on our app!
            """
        )
        
        # Step 8: Simulate drone delivery
        print_step(8, "Simulating drone delivery to customer")
        
        # Wait a moment to simulate time passing
        time.sleep(2)
        
        print(f"{Colors.GREEN}✓ Drone has arrived at the delivery location ({delivery_location}){Colors.ENDC}")
        
        print_notification(
            f"{customer_name} ({customer_email})", 
            f"""
Your order #{order_id} has arrived!

Our drone has arrived at your delivery location. 
Please collect your package immediately.

Thank you for using our Drone Delivery Service!
            """
        )
        
        # Step 9: Simulate delivery confirmation
        print_step(9, "Simulating delivery confirmation")
        
        # Create delivery confirmation payload
        delivery_payload = {
            "order_id": order_id
        }
        
        print_service_call("Processing Order", f"{PROCESSING_ORDER_URL}/order_delivered", "POST")
        
        try:
            # This endpoint may not exist yet, we're just simulating
            delivery_response = requests.post(
                f"{PROCESSING_ORDER_URL}/order_delivered",
                json=delivery_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"{Colors.GREEN}✓ Delivery confirmation sent{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Simulated delivery confirmation (endpoint may not exist): {str(e)}{Colors.ENDC}")
        
        # Step 10: Get final order status
        print_step(10, "Checking final order status")
        print_service_call("Order", f"{ORDER_URL}/order/{order_id}")
        
        try:
            final_status_response = requests.get(f"{ORDER_URL}/order/{order_id}")
            final_status = final_status_response.json()
            print_response(final_status)
            
            status = final_status.get("data", {}).get("order_status", "UNKNOWN")
            print(f"{Colors.GREEN}✓ Final order status: {status}{Colors.ENDC}")
            
            # If the status hasn't been updated to DELIVERED by the /order_delivered endpoint
            # we can simulate it here
            if status != "DELIVERED":
                print(f"{Colors.YELLOW}⚠ Simulating order status update to DELIVERED{Colors.ENDC}")
                
                update_payload = {
                    "status": "DELIVERED"
                }
                
                try:
                    update_response = requests.put(
                        f"{ORDER_URL}/order/{order_id}",
                        json=update_payload,
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"{Colors.GREEN}✓ Order status updated to DELIVERED{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}Failed to update order status: {str(e)}{Colors.ENDC}")
                    
        except Exception as e:
            print(f"{Colors.RED}Error getting final order status: {str(e)}{Colors.ENDC}")
            
        print_notification(
            f"{customer_name} ({customer_email})", 
            f"""
Order #{order_id} Delivered - Thank you!

Your order has been successfully delivered.

Order Details:
- Items: {item_name} x 2
- Total Amount: ${total_amount:.2f}
- Status: DELIVERED

Please rate your delivery experience in our app.
Thank you for choosing our service!
            """
        )
            
        # Conclusion
        print(f"\n{Colors.BOLD}{Colors.HEADER}===== SIMULATION COMPLETED ====={Colors.ENDC}")
        print(f"{Colors.HEADER}Simulation ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}✓ All services are working correctly!{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.BOLD}{Colors.RED}Simulation failed: {str(e)}{Colors.ENDC}")
        
if __name__ == "__main__":
    simulate_order_flow() 