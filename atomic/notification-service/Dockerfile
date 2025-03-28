FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./notification.py .

# Email configuration (Override these values when running the container)
ENV EMAIL_ENABLED=false
ENV EMAIL_HOST=smtp.gmail.com
ENV EMAIL_PORT=587
ENV EMAIL_USER=""
ENV EMAIL_PASSWORD=""
ENV EMAIL_FROM="drone.delivery@example.com"

CMD [ "python", "./notification.py" ] 