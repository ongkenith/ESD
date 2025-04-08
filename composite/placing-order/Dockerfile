# Start with the official Python 3.8 image
FROM python:3-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install the required dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY placing_order.py ./

# Define the command to run the app
CMD ["python", "./placing_order.py"]
