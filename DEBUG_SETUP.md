# Debugging Setup Guide

This project is configured for debugging with debugpy and Cursor/VS Code debugger.

## Prerequisites

- Docker and Docker Compose installed
- Cursor or VS Code with Python extension
- Environment variables configured (see `env.example`)

## Debugging Options

### 1. Debug Backend in Docker (Recommended)

This is the recommended approach as it matches the production environment.

**Steps:**

1. Open the project in Cursor/VS Code
2. Go to the Debug panel (Ctrl+Shift+D / Cmd+Shift+D)
3. Select "Debug Backend (Docker)" from the dropdown
4. Press F5 or click the play button
5. The debugger will:
   - Start the Docker container with debugpy
   - Wait for the debugger to attach
   - Connect to the running container

**Features:**

- Full Docker environment
- Hot reload enabled
- Debug port 5678 exposed
- Path mapping configured

### 2. Debug Backend Locally

For faster iteration without Docker overhead.

**Steps:**

1. Install dependencies: `pip install -r backend/requirements.txt`
2. Set environment variables
3. Select "Debug Backend (Local)" from debug dropdown
4. Press F5

### 3. Debug Frontend (Next.js)

**Steps:**

1. Select "Debug Frontend (Next.js)" from debug dropdown
2. Press F5

## Debugging Features

- **Breakpoints**: Set breakpoints in your Python code
- **Variable inspection**: Hover over variables or use the Variables panel
- **Call stack**: See the execution path
- **Console**: Use the Debug Console for evaluation
- **Step through**: Use F10 (step over), F11 (step into), Shift+F11 (step out)

## Troubleshooting

### Debugger won't connect

- Ensure Docker container is running: `docker-compose -f docker-compose.dev.yml ps`
- Check if port 5678 is available: `lsof -i :5678`
- Verify debugpy is installed in container: `docker-compose -f docker-compose.dev.yml exec backend pip list | grep debugpy`

### Container won't start

- Check logs: `docker-compose -f docker-compose.dev.yml logs backend`
- Rebuild container: `docker-compose -f docker-compose.dev.yml build backend`

### Environment variables

- Copy `env.example` to `.env` and fill in your API keys
- Restart containers after changing environment variables

## Useful Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Stop environment
docker-compose -f docker-compose.dev.yml down

# Rebuild backend
docker-compose -f docker-compose.dev.yml build backend
```

## Debug Configuration Files

- `.vscode/launch.json`: Debug configurations
- `.vscode/tasks.json`: Pre-launch tasks
- `backend/Dockerfile.dev`: Docker configuration with debugpy
- `docker-compose.dev.yml`: Docker Compose with debug port exposed
