# Project Setup Guide

Use this guide to set up the project on a new machine.

## Prerequisites
- Python 3.10+
- PostgreSQL
- Redis
- Git

## 1. Clone/Network
If you have access to the remote repo:
```bash
git clone <repo-url>
cd TaloraV2
git checkout backup/safe-point
```

## 2. Environment Setup
Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
# If using pip
pip install -r requirements.txt

# OR if using uv (recommended for speed)
pip install uv
uv pip install -r requirements.txt
```

## 3. Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
**IMPORTANT**: Edit `.env` and fill in your actual API keys (Groq, Gemini) and database credentials.

## 4. Database Setup
Make sure PostgreSQL and Redis are running.
```bash
# Example creation (adjust as needed)
createdb talora_db
```

## 5. Run the Application
```bash
uvicorn api.main:app --reload
```
