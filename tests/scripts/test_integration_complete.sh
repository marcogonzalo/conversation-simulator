#!/bin/bash

# Complete integration test script for voice conversation
# This script tests the full voice-to-voice integration

set -e

echo "🧪 Testing Complete Voice Conversation Integration"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with your OpenAI API key:"
    echo "OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env file"
    echo "Please add your OpenAI API key to the .env file:"
    echo "OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

echo "✅ Environment variables loaded"

# Check if backend is running
echo "🔍 Checking if backend is running..."
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "🚀 Starting backend..."
    docker-compose up -d backend
    echo "⏳ Waiting for backend to be ready..."
    sleep 10
fi

echo "✅ Backend is running"

# Copy test file to container
echo "📋 Copying test file to container..."
docker cp tests/integration/test_voice_conversation.py conversation-simulator-backend-1:/app/

# Run the voice conversation test
echo "🧪 Running voice conversation integration test..."
docker-compose exec backend python tests/integration/test_voice_conversation.py

echo "✅ Voice conversation integration test completed!"
echo ""
echo "🎉 Integration test summary:"
echo "- ✅ Backend services running"
echo "- ✅ OpenAI API configured"
echo "- ✅ Voice conversation flow tested"
echo "- ✅ WebSocket communication tested"
echo ""
echo "🚀 The voice-to-voice integration is ready!"
echo "You can now start the frontend and test the complete flow:"
echo "  npm run dev (in frontend directory)"
