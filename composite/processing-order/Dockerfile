FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY processing_order.py ./
COPY invokes.py ./
CMD [ "python", "./processing_order.py" ]
