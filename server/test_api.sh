#!/bin/bash

# Simple test script to verify the API endpoints using cURL
BASE_URL="http://localhost:5000"

echo "Starting API tests with cURL...\n"

# Test connection endpoint
echo "Testing /connection endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/connection")
status_code="${response: -3}"
echo "Status: $status_code"
if [ "$status_code" -eq 200 ]; then
    echo "✓ Connection test passed\n"
else
    echo "❌ Connection test failed\n"
    exit 1
fi

# Test root endpoint
echo "Testing / endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/")
status_code="${response: -3}"
response_body="${response%???}"
echo "Status: $status_code"
echo "Response: $response_body"
if [ "$status_code" -eq 200 ] && [ "$response_body" = "Hello world" ]; then
    echo "✓ Root endpoint test passed\n"
else
    echo "❌ Root endpoint test failed\n"
    exit 1
fi

# Test temperature endpoint
echo "Testing /temperature endpoint..."
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")
response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/temperature" \
    -H "Content-Type: application/json" \
    -d "{
        \"mac\": \"dd:cc:bb:aa:99:88\",
        \"temperature\": 23.2,
        \"humidity\": 50.6,
        \"timestamp\": \"$timestamp\"
    }")
status_code="${response: -3}"
response_body="${response%???}"
echo "Status: $status_code"
echo "Response: $response_body"
if [ "$status_code" -eq 200 ]; then
    echo "✓ Temperature endpoint test passed\n"
else
    echo "❌ Temperature endpoint test failed\n"
    exit 1
fi

# Test power status endpoint
echo "Testing /powerstatus endpoint..."
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")
response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/powerstatus" \
    -H "Content-Type: application/json" \
    -d "{
        \"mac\": \"dd:cc:bb:aa:99:88\",
        \"voltage\": 23.2,
        \"percentage\": 89.2,
        \"dischargerate\": 55,
        \"timestamp\": \"$timestamp\"
    }")
status_code="${response: -3}"
response_body="${response%???}"
echo "Status: $status_code"
echo "Response: $response_body"
if [ "$status_code" -eq 200 ]; then
    echo "✓ Power status endpoint test passed\n"
else
    echo "❌ Power status endpoint test failed\n"
    exit 1
fi

# Test reload locations endpoint
echo "Testing /reload-locations endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/reload-locations")
status_code="${response: -3}"
response_body="${response%???}"
echo "Status: $status_code"
echo "Response: $response_body"
if [ "$status_code" -eq 200 ]; then
    echo "✓ Reload locations test passed\n"
else
    echo "❌ Reload locations test failed\n"
    exit 1
fi

# Test input validation (invalid MAC address)
echo "Testing input validation..."
response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/temperature" \
    -H "Content-Type: application/json" \
    -d "{
        \"mac\": \"dd:cc\",
        \"temperature\": 23.2,
        \"humidity\": 50.6
    }")
status_code="${response: -3}"
response_body="${response%???}"
echo "Invalid MAC status: $status_code"
if [ "$status_code" -eq 422 ]; then
    echo "✓ Input validation test passed\n"
else
    echo "❌ Input validation test failed\n"
    exit 1
fi

echo "�� All tests passed!" 