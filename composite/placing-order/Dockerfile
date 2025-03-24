# Start with the official Python 3.8 image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY composite/placing-order/requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the atomic services (customer-service, item-service, order) and composite service
COPY atomic/customer-service /app/atomic/customer-service/
COPY atomic/item-service /app/atomic/item-service/
COPY atomic/order /app/atomic/order/
COPY composite/placing-order /app/composite/placing-order/

# Expose the port that the Flask app will run on
EXPOSE 5000

# Define the command to run the app
CMD ["python", "/app/composite/placing-order/placing_order.py"]