**TITLE**: Drone Delivery Service
**DESCRIPTION**: A service where customers orders from our store, and the drone will deliver it to them.

**PRE-REQUISITES**
1. Have docker running on your desktop (DockerHub)

**RUNNING THE SERVICE(S)**
1. Ensure that you are at the correct directory --> ESD
2. Open command prompt (on VSCode)
3. Type in "docker-compose up -d" to start running the service based on your respective docker-compose file
4. Go to a web browser and type in "https://ongkenith.github.io/ESD/". You should be redirected to the login page.
5. (If you have not created an account) At the login page, do create an account, where everything can be fake EXCEPT your email address (so that you will receive the notification)

**USE CASE 1 STEPS - Add items into order**
1. Go to "Products" and "Add to cart" items you want to purchase
2. Proceed to "My Cart" and fill in a postal code before "Proceed to Checkout". It will take a while before the website starts loading
    - If you face an error saying no drone is available, please refer to the Troubleshooting section below to refresh the drone_status of all drones to be Available. We did not implement the functionality of having an automatic timer to continuously look through the drones_status to assign an available drone to a pending order as it is not part of our use case
3. You will be redirected to Paypal page to pay for your purchases. Log in with these details
    - Paypal account: sb-iiaqd38594568@personal.example.com
    - Password: O?5)QWKc
4. Once you have completed payment with Paypal, you will be redirected back to the website, where you may have to login again

**USE CASE 2 STEPS - Processing order**
1. Behind the scenes, the service will check when conditions are ideal to do the delivery
2. In "My Orders", you should be able to see the order statuses

**USE CASE 3 STEPS - Drone deliver order to your location**
1. When the parcel reached the delivery location:
&nbsp;&nbsp;&nbsp;&nbsp;- An email notification will be sent
&nbsp;&nbsp;&nbsp;&nbsp;- In "My Orders", the order should have changed it status
2. After collecting the parcel, return to the website and click "Received"
3. To initiate the use case, send a POST request to http://localhost:5400/order_delivered on POSTMAN with an order_id to mimic the arrival of a parcel

**Troubleshooting**
- I seem to have issues composing the Docker files from docker-compose? Keep getting ModuleNotFoundError. <br>
Answer: Clear all cache (Docker, Web browser) and restart VScode before trying to compose again
- I do not receive any notification email <br>
Answer: If you are grading this after XXX, the free trial API for the email has expired. Please follow the following steps to get an API key and add it to .env file <br>
&nbsp;&nbsp;&nbsp;&nbsp;1. Sign up for an account at https://www.mailersend.com/signup to have an account with trial plan <br>
&nbsp;&nbsp;&nbsp;&nbsp;2. At Email > Domains, click 'Manage' on the right hand side of the default domain you have <br>
&nbsp;&nbsp;&nbsp;&nbsp;3. Under API token, click on 'Generate new token' <br>
&nbsp;&nbsp;&nbsp;&nbsp;4. In the env file, change MAILERSEND_API_KEY to the new API key <br>
&nbsp;&nbsp;&nbsp;&nbsp;5. Under SMTP, click on 'Generate new user' <br>
&nbsp;&nbsp;&nbsp;&nbsp;6. In the env file, change EMAIL_PASSWORD to SMTP user's password. Change EMAIL_USER and EMAIL_FROM to SMTP user's username <br>
- All drones seem to be used, as my order is "Pending for delivery". If I want to reset drones to "Avaliable" so that I can test your other services, what should I do? <br>
Answer: Run reset_drone.py to reset all the drones to "Available"