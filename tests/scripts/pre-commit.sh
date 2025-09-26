#!/bin/bash

# Pre-commit script for Conversation Simulator
# Applies linting, formatting, and testing rules

set -e

echo "�� Running pre-commit checks..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root"
    exit 1
fi

# Backend checks
echo "🐍 Checking backend..."
cd backend

# Type checking
echo "  📝 Type checking with mypy..."
python -m mypy src/ --ignore-missing-imports

# Linting
echo "  🔍 Linting with flake8..."
python -m flake8 src/ --max-line-length=88 --extend-ignore=E203,W503

# Formatting check
echo "  🎨 Checking code formatting with black..."
python -m black --check src/

# Import sorting check
echo "  📦 Checking import sorting with isort..."
python -m isort --check-only src/

# Run tests
echo "  �� Running tests..."
python -m pytest tests/ -v --cov=src --cov-fail-under=80

cd ..

# Frontend checks
echo "⚛️ Checking frontend..."
cd frontend

# Type checking
echo "  📝 Type checking with TypeScript..."
npm run type-check

# Linting
echo "  🔍 Linting with ESLint..."
npm run lint

# Formatting check
echo "  🎨 Checking code formatting with Prettier..."
npx prettier --check "src/**/*.{js,jsx,ts,tsx,json,css,md}"

# Run tests
echo "  🧪 Running tests..."
npm run test:coverage

cd ..

echo "✅ All pre-commit checks passed!"
