# Test Suite - Conversation Simulator

## Overview

This directory contains the complete test suite for the Conversation Simulator project, including unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── scripts/                    # Test execution scripts
│   ├── run-tests.sh           # Main test runner
│   ├── test-backend.sh        # Backend tests only
│   ├── test-frontend.sh       # Frontend tests only
│   └── test-integration.sh    # Integration tests only
├── integration/               # Integration tests
│   └── test_voice_conversation.py
└── README.md                  # This file
```

## Test Types

### 1. Backend Tests

- **Location**: `backend/tests/`
- **Framework**: pytest
- **Coverage**: 80%+ target
- **Includes**:
  - Unit tests for services
  - API endpoint tests
  - WebSocket tests
  - Database tests

### 2. Frontend Tests

- **Location**: `frontend/src/**/__tests__/`
- **Framework**: Jest + React Testing Library
- **Coverage**: 80%+ target
- **Includes**:
  - Component tests
  - Hook tests
  - Service tests
  - Integration tests

### 3. Integration Tests

- **Location**: `tests/integration/`
- **Framework**: Python + pytest
- **Includes**:
  - End-to-end voice conversation flow
  - WebSocket communication tests
  - Audio processing tests

## Running Tests

### Prerequisites

1. Docker and Docker Compose installed
2. Environment variables set (see `.env.example`)

### Quick Start

```bash
# Run all tests
./tests/scripts/run-tests.sh

# Run specific test types
./tests/scripts/run-tests.sh --type backend
./tests/scripts/run-tests.sh --type frontend
./tests/scripts/run-tests.sh --type integration

# Run without coverage
./tests/scripts/run-tests.sh --no-coverage

# Run with verbose output
./tests/scripts/run-tests.sh --verbose
```

### Individual Test Suites

```bash
# Backend only
./tests/scripts/test-backend.sh

# Frontend only
./tests/scripts/test-frontend.sh

# Integration only
./tests/scripts/test-integration.sh
```

### Manual Docker Commands

```bash
# Backend tests
docker-compose -f docker-compose.test.yml run --rm backend-test

# Frontend tests
docker-compose -f docker-compose.test.yml run --rm frontend-test

# Integration tests
docker-compose -f docker-compose.test.yml up -d backend frontend test-db
docker-compose -f docker-compose.test.yml run --rm integration-test
docker-compose -f docker-compose.test.yml down
```

## Test Configuration

### Backend (pytest)

- **Config**: `backend/pytest.ini`
- **Coverage**: HTML and terminal reports
- **Parallel**: Uses pytest-xdist for parallel execution
- **Mocking**: pytest-mock for service mocking

### Frontend (Jest)

- **Config**: `frontend/jest.config.js`
- **Setup**: `frontend/jest.setup.js`
- **Coverage**: LCOV and HTML reports
- **Mocking**: Jest mocks for Web APIs

### Integration

- **Database**: PostgreSQL test database
- **Services**: Full stack with mocked external APIs
- **Audio**: Mocked audio processing

## Coverage Reports

After running tests, coverage reports are generated:

- **Backend**: `backend/htmlcov/index.html`
- **Frontend**: `frontend/coverage/lcov-report/index.html`

## Test Data

### Mock Data

- **Personas**: Test personas for different scenarios
- **Conversations**: Sample conversation data
- **Audio**: Mock audio files for testing

### Test Database

- **Type**: PostgreSQL
- **Port**: 5433 (to avoid conflicts)
- **Database**: `conversation_simulator_test`
- **User**: `test_user`
- **Password**: `test_password`

## Continuous Integration

### GitHub Actions (Future)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: ./tests/scripts/run-tests.sh
```

## Debugging Tests

### Backend

```bash
# Run with debug output
docker-compose -f docker-compose.test.yml run --rm backend-test pytest tests/ -v -s

# Run specific test
docker-compose -f docker-compose.test.yml run --rm backend-test pytest tests/test_audio_service.py::test_audio_processing -v
```

### Frontend

```bash
# Run with debug output
docker-compose -f docker-compose.test.yml run --rm frontend-test npm run test -- --verbose

# Run specific test
docker-compose -f docker-compose.test.yml run --rm frontend-test npm run test -- --testNamePattern="ConversationInterface"
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies (APIs, databases)
3. **Coverage**: Aim for 80%+ coverage
4. **Performance**: Tests should run quickly
5. **Reliability**: Tests should be deterministic
6. **Documentation**: Write clear test descriptions

## Troubleshooting

### Common Issues

1. **Docker not running**: Start Docker Desktop
2. **Port conflicts**: Check if ports 3000, 8000, 5433 are free
3. **Permission errors**: Run `chmod +x tests/scripts/*.sh`
4. **Environment variables**: Check `.env` file exists

### Cleanup

```bash
# Clean up test containers and volumes
docker-compose -f docker-compose.test.yml down -v

# Remove test images
docker rmi conversation-simulator_backend-test
docker rmi conversation-simulator_frontend-test
docker rmi conversation-simulator_integration-test
```
