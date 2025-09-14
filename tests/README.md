# Tests

This directory contains all test files and scripts for the Conversation Simulator project.

## Structure

```
tests/
├── scripts/                    # Test scripts
│   ├── docker-dev.sh          # Docker development helper
│   └── test_integration_complete.sh  # Complete integration test
├── integration/               # Integration tests
│   └── test_voice_conversation.py  # Voice conversation integration test
└── README.md                  # This file
```

## Usage

### Development Scripts

#### Docker Development Helper
```bash
# From project root
./tests/scripts/docker-dev.sh [start|stop|restart|logs|status|rebuild]
```

**Commands:**
- `start` - Start all services (default)
- `stop` - Stop all services
- `restart` - Restart all services
- `logs` - Show logs
- `status` - Show service status
- `rebuild` - Rebuild and start services

#### Complete Integration Test
```bash
# From project root
./tests/scripts/test_integration_complete.sh
```

This script will:
1. Check environment variables
2. Start backend services if needed
3. Run the complete voice conversation integration test
4. Report results

### Integration Tests

#### Voice Conversation Test
```bash
# Run directly
python tests/integration/test_voice_conversation.py

# Or via Docker
docker-compose exec backend python tests/integration/test_voice_conversation.py
```

This test verifies:
- Persona loading
- Conversation creation
- WebSocket communication
- Audio message handling
- Voice conversation flow

## Prerequisites

- Docker and Docker Compose
- OpenAI API key in `.env` file
- Backend services running (or script will start them)

## Environment Variables

Required in `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

## Troubleshooting

### Backend Not Starting
- Check Docker is running
- Verify `.env` file exists and has required variables
- Check port 8000 is not in use

### WebSocket Connection Failed
- Ensure backend is running on port 8000
- Check firewall settings
- Verify WebSocket endpoint is accessible

### Audio Test Fails
- Verify OpenAI API key is valid
- Check internet connection
- Ensure audio format is supported
