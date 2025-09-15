#!/bin/bash

# Frontend test runner
set -e

echo "⚛️ Running frontend tests..."

# Build and run frontend tests
docker-compose -f docker-compose.test.yml run --rm frontend-test

echo "✅ Frontend tests completed!"
