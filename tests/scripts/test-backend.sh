#!/bin/bash

# Backend test runner
set -e

echo "🐍 Running backend tests..."

# Build and run backend tests
docker-compose -f docker-compose.test.yml run --rm backend-test

echo "✅ Backend tests completed!"
