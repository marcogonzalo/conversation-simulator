#!/bin/bash

echo "🚀 Testing Conversation Simulator Setup"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys before running the application."
fi

echo "✅ Environment file ready"

# Check if required directories exist
if [ ! -d "backend/data" ]; then
    echo "📁 Creating backend data directories..."
    mkdir -p backend/data/personas
    mkdir -p backend/data/conversations
    mkdir -p backend/data/analyses
fi

echo "✅ Data directories ready"

# Test Docker Compose configuration
echo "🔧 Testing Docker Compose configuration..."
if docker-compose config > /dev/null 2>&1; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "❌ Docker Compose configuration has errors"
    exit 1
fi

echo ""
echo "🎉 Setup test completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - ELEVENLABS_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_ANON_KEY"
echo ""
echo "2. Start the application:"
echo "   docker-compose -f docker-compose.dev.yml up --build"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For more information, see README.md"
