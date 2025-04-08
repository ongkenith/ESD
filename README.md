**TITLE**: Drone Delivery Service
**DESCRIPTION**: A service where customers orders from our store, and the drone will deliver it to them.

**PRE-REQUISITES**
1. Have docker running on your desktop (DockerHub)

**RUNNING THE SERVICE(S)**
1. Go to ESD/SQL/SuperScript.sql and run the SQL script
2. Ensure that you are at the correct directory --> ESD
3. Open command prompt (on VSCode)
4. Type in "docker-compose up -d" to start running the service based on your respective docker-compose file
5. Go to a web browser and type in "https://ongkenith.github.io/ESD/". You should be redirected to the login page.
6. (If you have not created an account) At the login page, do create an account, where everything can be not real EXCEPT your email address (so that you will receive the notification)

**USE CASE 1 STEPS - Add items into order**
1. Go to "Products" and "add to cart" items you want to purchase
2. Proceed to "My Cart" and fill in a postal code before "Proceed to Checkout". It will take a while before the website starts loading
3. You will be redirected to Paypal page to pay for your purchases. Log in with these details
    - Paypal account: sb-iiaqd38594568@personal.example.com
    - Password: O?5)QWKc
4. Once you have completed payment with Paypal, you will be redirected back to the website

**USE CASE 2 STEPS - Processing order**
1. Behind the scenes, the service will check when conditions are ideal to do the delivery
2. In "My Orders", you should be able to see the order statuses

**USE CASE 3 STEPS - Drone deliver order to your location**
1. When the parcel reached the delivery location:
    - An email notification will be sent
    - In "My Orders", the order should have changed it status
2. After collecting the parcel, return to the website and click "Received"

**Troubleshooting**
- I seem to have issues composing the Docker files from docker-compose? Keep getting ModuleNotFoundError.
Answer: Clear all cache (Docker, Web browser) and restart VScode before trying to compose again
- I do not receive any notification email
Answer: If you are grading this after XXX, the free trial API for the email has expired. Please follow the following steps to get an API key and add it to .env file <br>
&nbsp;&nbsp;&nbsp;&nbsp;1. 