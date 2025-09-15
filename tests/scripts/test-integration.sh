#!/bin/bash

# Integration test runner
set -e

echo "🔗 Running integration tests..."

# Start services
docker-compose -f docker-compose.test.yml up -d backend frontend test-db

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Run integration tests
docker-compose -f docker-compose.test.yml run --rm integration-test

# Cleanup
docker-compose -f docker-compose.test.yml down

echo "✅ Integration tests completed!"
