# Backend Setup & Deployment Guide

**For Backend Team Members**

This guide will help you:
1. Clone and set up the backend locally
2. Configure environment variables
3. Deploy to production
4. Provide the API URL to the frontend team

---

## 1. Initial Setup (First Time)

### Clone the Repository
```bash
git clone https://github.com/theravikumar/TaloraV2.git
cd TaloraV2
```

### Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your settings:

```bash
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database (PostgreSQL)
DATABASE_URL=postgresql://talora:talora_password@localhost:5432/talora_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (IMPORTANT: Generate a secure key)
# Run this command to generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your_generated_secret_key_here

# API Configuration (Development)
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True
```

### Setup Database

```bash
# Start PostgreSQL (if using Docker)
docker run -d \
  --name talora-postgres \
  -e POSTGRES_USER=talora \
  -e POSTGRES_PASSWORD=talora_password \
  -e POSTGRES_DB=talora_db \
  -p 5432:5432 \
  postgres:15

# Start Redis (if using Docker)
docker run -d \
  --name talora-redis \
  -p 6379:6379 \
  redis:7
```

### Run Database Migrations
```bash
# Create tables
# (Run your migration script if you have one)
# For now, tables are created automatically on first run
```

### Seed Database with Test Jobs
```bash
python scripts/seed_jobs.py
```

### Start the Backend Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Verify It's Running
```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected","redis":"connected"}
```

---

## 2. What You Need to Know

### Backend Configuration Locations

| What | Where | What to Change |
|------|-------|----------------|
| Server Host/Port | api/config.py lines 13-14 | api_host, api_port |
| Environment Variables | .env file | Database URLs, API keys |
| CORS Settings | api/main.py line 22 | Allowed origins for frontend |
| Database Schema | Auto-created on startup | N/A |

### Important Files

- api/main.py - Main FastAPI application (server entry point)
- api/config.py - Configuration management (reads from .env)
- .env - Environment variables (secrets, database URLs)
- api/routes/ - API endpoints (auth, resume, jobs, match)
- api/services/ - Business logic (auth, job search, etc.)

---

## 3. Local Development

### Running the Backend

Method 1: Using uvicorn directly (Recommended)
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Method 2: Using Python
```bash
python api/main.py
```

Method 3: Using the run script
```bash
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh
```

### Testing the API

Run the end-to-end tests:
```bash
chmod +x scripts/test_e2e.sh
./scripts/test_e2e.sh
```

### Check Logs
```bash
# If running in background
tail -f /tmp/talora_api.log
```

---

## 4. Production Deployment

### General Deployment Steps

1. Choose a cloud platform or server provider
2. Set up PostgreSQL and Redis databases
3. Configure environment variables
4. Deploy the application code
5. Configure HTTPS/SSL
6. Get the production URL
7. Update CORS settings

### Environment Variables for Production

Set these in your cloud platform's configuration:

```bash
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
JWT_SECRET_KEY=your_generated_secret_key
API_DEBUG=False
DATABASE_URL=postgresql://user:password@host:5432/database
REDIS_URL=redis://host:6379/0
```

### Common Deployment Patterns

#### Pattern 1: Platform-as-a-Service (PaaS)

Most PaaS platforms require a Procfile:

Create a file named `Procfile`:
```
web: uvicorn api.main:app --host=0.0.0.0 --port=$PORT
```

Steps:
1. Connect your GitHub repository to the platform
2. Set environment variables through the platform UI
3. Platform auto-detects Python and installs dependencies
4. Platform provides a URL like: https://your-app.platform-domain.com

#### Pattern 2: Virtual Private Server (VPS)

1. Provision a server (Ubuntu 22.04 recommended)
2. SSH into the server
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip postgresql redis-server nginx
```

4. Clone repository and setup:
```bash
git clone https://github.com/theravikumar/TaloraV2.git
cd TaloraV2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

5. Configure environment:
```bash
cp .env.example .env
nano .env  # Edit with production values
```

6. Create systemd service file at `/etc/systemd/system/talora-api.service`:
```ini
[Unit]
Description=Talora API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/TaloraV2
Environment="PATH=/path/to/TaloraV2/.venv/bin"
ExecStart=/path/to/TaloraV2/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

7. Start service:
```bash
sudo systemctl enable talora-api
sudo systemctl start talora-api
```

8. Configure Nginx as reverse proxy
9. Set up SSL certificate (using Let's Encrypt or similar)
10. Your URL: https://api.yourdomain.com

#### Pattern 3: Container-Based Deployment

Create a Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and deploy using your container orchestration platform.

---

## 5. Critical: CORS Configuration for Frontend

### Location: api/main.py (line 19-26)

IMPORTANT: Update CORS before production deployment

Current (Development):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Production (Change to):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",           # Your frontend domain
        "https://www.yourdomain.com",       # With www
        "http://localhost:3000",            # For local frontend testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Why This Matters:
- Frontend runs at: https://yourdomain.com
- Backend runs at: https://api.yourdomain.com
- CORS allows frontend to call backend from different domain
- Without correct CORS, frontend will get errors like "blocked by CORS policy"

---

## 6. Providing Info to Frontend Team

### After Deployment, Send Frontend Team:

1. Production API Base URL
```
Backend URL: https://api.yourdomain.com
```

2. API Documentation
Send them: FRONTEND_API_GUIDE.md

3. Example .env for Frontend
```bash
# For their frontend project
REACT_APP_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

4. Health Check Endpoint
```bash
curl https://api.yourdomain.com/health
```

---

## 7. Environment Variables Reference

### Required in .env

```bash
# LLM API Keys (at least one required)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis
REDIS_URL=redis://host:6379/0

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your_secret_key_minimum_32_characters_long

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False  # Set to False in production
```

### Optional in .env

```bash
# LLM Models
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_MODEL=gemini-2.0-flash
OLLAMA_MODEL=llama3.2:latest

# File Upload
MAX_UPLOAD_SIZE_MB=10
UPLOAD_DIR=data/uploads

# Session
SESSION_TIMEOUT_MINUTES=5
JWT_EXPIRATION_HOURS=24

# Ollama (if using local LLM)
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 8. Common Issues & Solutions

### Issue 1: Port Already in Use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn api.main:app --port 8001
```

### Issue 2: Database Connection Failed
```bash
# Check PostgreSQL is running
psql -h localhost -U talora -d talora_db

# Check DATABASE_URL in .env is correct
```

### Issue 3: Redis Connection Failed
```bash
# Check Redis is running
redis-cli ping  # Should return "PONG"

# Check REDIS_URL in .env is correct
```

### Issue 4: LLM API Errors
```bash
# Groq rate limit: Wait or use Ollama fallback
# Gemini quota: Wait 24 hours or use paid tier
# Ollama not running: Start Ollama service

# Test LLM providers
python -c "from shared.llm.router import llm_router; llm_router.test_all()"
```

### Issue 5: Frontend Can't Connect (CORS)
```bash
# Update CORS in api/main.py
# Add frontend domain to allow_origins list
```

---

## 9. Checklist Before Giving to Frontend

- [ ] Backend deployed and accessible
- [ ] Health check returns {"status": "healthy"}
- [ ] Database connected
- [ ] Redis connected
- [ ] Test user registration works
- [ ] Test user login works
- [ ] Test resume upload works
- [ ] Test job search returns results
- [ ] CORS configured with frontend domain
- [ ] Environment variables set in production
- [ ] SSL certificate configured (HTTPS)
- [ ] API URL shared with frontend team
- [ ] FRONTEND_API_GUIDE.md shared with frontend

---

## 10. Quick Commands Reference

```bash
# Start backend (development)
uvicorn api.main:app --reload

# Start backend (production)
uvicorn api.main:app --host 0.0.0.0 --port 80

# Run tests
./scripts/test_e2e.sh

# Check health
curl http://localhost:8000/health

# View logs
tail -f /tmp/talora_api.log

# Stop all uvicorn processes
pkill -f uvicorn

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Support & Documentation

- API Documentation: /FRONTEND_API_GUIDE.md
- Main README: /README.md
- Setup Guide: /SETUP_GUIDE.md
- GitHub Repo: https://github.com/theravikumar/TaloraV2

---

Last Updated: Feb 11, 2026  
Backend Status: Production Ready  
Version: 1.0.0
