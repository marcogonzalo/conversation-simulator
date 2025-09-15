#!/bin/bash

# Test runner script for Docker environment
set -e

echo "🧪 Starting test suite..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Parse command line arguments
TEST_TYPE="all"
COVERAGE=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --type TYPE        Test type: all, backend, frontend, integration"
            echo "  --no-coverage      Disable coverage reporting"
            echo "  --verbose          Enable verbose output"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build test images
print_status "Building test images..."
docker-compose -f docker-compose.test.yml build

# Run tests based on type
case $TEST_TYPE in
    "backend")
        print_status "Running backend tests..."
        docker-compose -f docker-compose.test.yml run --rm backend-test
        ;;
    "frontend")
        print_status "Running frontend tests..."
        docker-compose -f docker-compose.test.yml run --rm frontend-test
        ;;
    "integration")
        print_status "Running integration tests..."
        docker-compose -f docker-compose.test.yml up -d backend frontend test-db
        sleep 10  # Wait for services to be ready
        docker-compose -f docker-compose.test.yml run --rm integration-test
        docker-compose -f docker-compose.test.yml down
        ;;
    "all")
        print_status "Running all tests..."
        
        # Run backend tests
        print_status "Running backend tests..."
        docker-compose -f docker-compose.test.yml run --rm backend-test
        
        # Run frontend tests
        print_status "Running frontend tests..."
        docker-compose -f docker-compose.test.yml run --rm frontend-test
        
        # Run integration tests
        print_status "Running integration tests..."
        docker-compose -f docker-compose.test.yml up -d backend frontend test-db
        sleep 10  # Wait for services to be ready
        docker-compose -f docker-compose.test.yml run --rm integration-test
        docker-compose -f docker-compose.test.yml down
        ;;
    *)
        print_error "Invalid test type: $TEST_TYPE"
        print_error "Valid types: all, backend, frontend, integration"
        exit 1
        ;;
esac

print_status "Test suite completed successfully! 🎉"

# Show coverage reports if enabled
if [ "$COVERAGE" = true ]; then
    print_status "Coverage reports generated:"
    echo "  - Backend: backend/htmlcov/index.html"
    echo "  - Frontend: frontend/coverage/lcov-report/index.html"
fi
