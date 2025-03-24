# Order Processing System Test Suite

This directory contains a suite of test scripts designed to verify the functionality of the Order Processing System, including:
- Weather condition checking
- Order processing flow
- Notification services (API and RabbitMQ)

## Test Scripts

### Individual Component Tests

1. **Weather Check Test (`test_weather_check.py`)**
   - Tests the condition-check service that verifies if weather conditions are suitable for drone flight
   - Sends a request with pickup and delivery locations
   - Outputs weather data and suitability status

2. **Notification Service Test (`test_notification_service.py`)**
   - Tests both notification methods:
     - Direct HTTP API endpoint
     - RabbitMQ queue-based notifications
   - Verifies that notifications are properly sent and processed

3. **Order Processing Test (`test_process_order.py`)**
   - Tests the process_order endpoint
   - Sends an order for processing
   - Verifies the response and order status

### Integrated Tests

4. **Full Order Flow Test (`test_full_order_flow.py`)**
   - Simulates the complete order processing flow
   - Includes weather check, order processing, and notifications
   - Provides detailed output for each step

### Master Test Runner

5. **Complete Test Suite (`run_complete_tests.py`)**
   - Runs all the individual tests in sequence
   - Provides a summary of all test results
   - Reports overall success/failure status

## Running Tests

### Local Testing

To run tests against services running on localhost:

```
python run_complete_tests.py
```

### Docker Testing

To run tests against services running in Docker containers:

```
python run_complete_tests.py --docker
```

### Individual Tests

You can also run individual tests separately:

```
python test_weather_check.py [--docker] [--pickup LOCATION] [--delivery LOCATION]
python test_notification_service.py [--docker] [--api-only | --queue-only] [--customer ID] [--order ID] [--message "Custom message"]
python test_process_order.py [--docker] [ORDER_ID]
python test_full_order_flow.py [--docker]
```

## Environment Requirements

These tests require:
1. Python 3.6+
2. Required packages: `requests`, `pika`, `json`
3. All services (order processing, condition check, notification) running
4. RabbitMQ server running and accessible

## Expected Output

Successful tests will display:
- ✅ Status indicators for successful operations
- Detailed output of API responses
- Summary of test results

Failed tests will show:
- ❌ Error indicators
- Reasons for failure
- Error messages from services 