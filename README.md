**TITLE**: Drone Delivery Service
**DESCRIPTION**: A service where customers orders from our store, and the drone will deliver it to them.

**PRE-REQUISITES**
1. Have docker running on your desktop (DockerHub)

**RUNNING THE SERVICE(S)**
1. Go to ESD/SQL/SuperScript.sql and run the SQL script
2. Ensure that you are at the correct directory --> ESD
3. Open command prompt (on VSCode)
4. Type in "docker-compose up -d" to start running the service based on your respective docker-compose file
5. Open up login.html and log in to an account
    - Username: 
    - Password:

**USE CASE 1 STEPS - Add items into order**
1. Go to "Store" and "add to cart" items you want to purchase
2. Proceed to "My Cart" and fill in the details of delivery information before "Proceed to Checkout"
    - Input a legit email address so that you can receive the notification later on
3. You will be redirected to Paypal page to pay for your purchases
    - Paypal account: sb-iiaqd38594568@personal.example.com
    - Password: O?5)QWKc
4. Once you have completed payment with Paypal, you will be redirected back to the website

**USE CASE 2 STEPS - Processing order**
1. Behind the scenes, the service will check when conditions are ideal to do the delivery
2. In "My Orders", you should be able to see the order statuses

**USE CASE 3 STEPS - Drone deliver order to your location**
1. 5 minutes before reaching the destination, you should receive an email notification
2. When the parcel reached the delivery location:
    - An email notification will be sent
    - In "My Orders", the order should have changed it status
3. After collecting the parcel, return to the website and click "Received"

**Troubleshooting**
- I seem to have issues composing the Docker files from docker-compose? Keep getting ModuleNotFoundError.
Answer: Clear all cache (Docker, Web browser) and restart VScode before trying to compose again