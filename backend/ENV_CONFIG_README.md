# Environment Configuration Files

This directory contains environment-specific configuration files for different deployment scenarios.

## File Structure

```
Project Root:
├── .env                     # Application configuration (API keys, models, audio settings)
├── env.example              # Template for .env file
│
└── backend/
    ├── docker.env           # Docker container environment settings
    ├── docker.env.example   # Template and documentation for docker.env
    ├── development.env      # Local development environment settings  
    ├── production.env       # Production deployment settings (Supabase by default)
    └── ENV_CONFIG_README.md # This file - configuration documentation
```

## Configuration Philosophy

**Separation of Concerns:**

### Root `.env` file
Contains **application-level configuration** that is consistent across environments:
- API keys (OpenAI, external services)
- Model configurations (GPT models, voice models)
- Audio settings (channels, sample rate)
- Voice detection parameters

### Environment `.env` files (`backend/`)
Contains **environment-specific configuration**:
- Database connection (via `DATABASE_URL`)
- Debug flags
- Log levels
- Environment identifiers

> **Important:** Always use `DATABASE_URL` for database configuration.

## Usage

### For Docker Development
The `docker-compose.yml` loads both:
1. Root `.env` - Application settings
2. `backend/docker.env` - Docker-specific settings

### For Other Environments
Specify the appropriate environment file when running the application:

```bash
# Development (local)
cd backend
python -m uvicorn src.main:app --env-file development.env

# Production (Supabase or custom PostgreSQL)
cd backend
python -m uvicorn src.main:app --env-file production.env
```

## Priority Order

When multiple `.env` files are loaded, **later files override earlier ones**:
1. Root `.env` (loaded first - application settings)
2. Environment-specific `.env` (loaded second - environment settings)

**Important:** Environment-specific files should NOT override application settings like API keys or model configurations. They should only define environment-specific values like database connections.

## Security Notes

- ⚠️ **Never commit actual API keys or passwords**
- ✅ Use `env.example` as a template
- ✅ Keep sensitive data in root `.env` which is gitignored
- ✅ Environment files can be committed as they contain only placeholders

## Quick Start

### 1. Setup Application Configuration
```bash
# Copy template
cp env.example .env

# Edit and add your OpenAI API key
nano .env
```

### 2. Setup Environment Configuration
```bash
# For Docker development
cp backend/docker.env.example backend/docker.env
# (Usually no changes needed for Docker)

# For local development
cp backend/docker.env.example backend/development.env
# Edit DATABASE_URL if needed

# For production
cp backend/docker.env.example backend/production.env
# Configure Supabase or PostgreSQL connection
```

### 3. Start Application
```bash
# With Docker
docker-compose up

# Without Docker (local)
cd backend
python -m uvicorn src.main:app --env-file development.env
```

## Troubleshooting

### API Key Not Working
- Check that `OPENAI_API_KEY` is in root `.env`, not in `backend/*.env`
- Verify the key starts with `sk-proj-` or `sk-`
- Restart Docker containers after changing `.env`: `docker-compose restart`

### Database Connection Issues
- Check `DATABASE_URL` format in `backend/docker.env`
- For Docker, use hostname `postgres` (service name)
- For host machine, use `host.docker.internal`
- Verify PostgreSQL container is running: `docker-compose ps`

### Environment Variables Not Loading
- Ensure files are named exactly: `docker.env`, `development.env`, `production.env`
- Check file is referenced in `docker-compose.yml` under `env_file`
- Verify no syntax errors in `.env` files (no spaces around `=`)
