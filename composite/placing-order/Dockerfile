# Start with the official Python 3.8 image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .  

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copying files from within placing-order directory (atomic services)
# COPY ./customer-service /app/atomic/customer-service/
# COPY ./item-service /app/atomic/item-service/
# COPY ./order /app/atomic/order/
COPY . /app/composite/placing-order/

# Expose the port that the Flask app will run on
EXPOSE 5000

# Define the command to run the app
CMD ["python", "/app/composite/placing-order/placing_order.py"]
