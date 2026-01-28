#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <openrouter-api-key>"
    exit 1
fi

API_KEY="$1"

echo "Checking OpenRouter API key..."

response=$(curl -s -w "%{http_code}" -o /tmp/openrouter_check.json \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    https://openrouter.ai/api/v1/models)

http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✓ API key is valid"
    echo "Available models: $(jq -r '.data | length' /tmp/openrouter_check.json 2>/dev/null || echo "N/A")"
else
    echo "✗ API key is invalid or error occurred"
    echo "HTTP Status: $http_code"
    if [ -f /tmp/openrouter_check.json ]; then
        echo "Response: $(cat /tmp/openrouter_check.json)"
    fi
fi

rm -f /tmp/openrouter_check.json