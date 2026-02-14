# TaloraV2 Setup & Run Guide

This guide details how to set up the **TaloraV2** (Backend) and **TaloraV2-ui-preview** (Frontend) repositories, specifically for the new scraper and search features.

## 1. Prerequisites

Ensure you have the following installed on your system:
*   **Git**
*   **Python 3.10+** (Recommend managing with `pyenv`)
*   **Node.js 18+** & **npm**
*   **uv** (Fast Python package installer - `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## 2. Clone & Setup Repositories

Create a project directory and clone both repositories side-by-side.

```bash
mkdir talora-project
cd talora-project

# 2.1 Backend (TaloraV2)
git clone -b feature/updated-backend-script https://github.com/theravikumar/TaloraV2.git
cd TaloraV2

# Create Virtual Environment & Install Dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Create .env file
cp .env.example .env
# EDITOR NOTE: You MUST update .env with your actual API keys:
# - GROQ_API_KEY
# - GEMINI_API_KEY
# - DATABASE_URL (If using Postgres, otherwise defaults to sqlite in code usually)

cd ..

# 2.2 Frontend (TaloraV2-ui-preview)
git clone -b feature/enhanced-search-filters https://github.com/theravikumar/TaloraV2-ui-preview.git
cd TaloraV2-ui-preview

# Install Dependencies
npm install
cd ..
```

## 3. Database Initialization (Backend)

The project currently uses SQLite for simplicity in the scraper script. 

```bash
cd TaloraV2
source .venv/bin/activate
# Ensure data directory exists
mkdir -p data

# Initialize DB (This happens automatically when you run the scraper, but good to know)
# data/jobs.db will be created.
```

## 4. Running the Scraper

To populate the database with jobs (using the new worldwide RemoteOK scraper with AI descriptions):

```bash
cd TaloraV2
source .venv/bin/activate

# Run the dedicated scraper script
python run_remoteok_scraper.py
```
*   **Expected Output**: It will fetch jobs from RemoteOK, generate cleaner descriptions using LLM (Groq/Ollama), and save them to `data/jobs.db`.
*   **Note**: This script uses **Groq** by default for speed. Ensure `GROQ_API_KEY` is set in `.env`.

## 5. Running the Application

You need to run both the Backend API and Frontend UI.

### Terminal 1: Backend API

```bash
cd TaloraV2
source .venv/bin/activate

# Run FastAPI server
# Note: Ensure the app references the correct DB path. 
# If main.py expects postgres/redis, you might need to adjust .env or run docker-compose.
# For this specific feature test, we assume the API reads from the sqlite or configured DB.

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
*(Check `api/main.py` or `api/services/job_service.py` to ensure it points to `data/jobs.db` or your configured `DATABASE_URL`)*

### Terminal 2: Frontend UI

```bash
cd TaloraV2-ui-preview

# Run Next.js Dev Server
npm run dev
```

## 6. Verification

1.  Open **Frontend**: [http://localhost:3000](http://localhost:3000)
2.  **Job List**: You should see the jobs scraped in Step 4.
3.  **Job Detail**: Click a job. It should show the **clean, AI-generated description**.
4.  **Apply**: Click the "Apply Now" button to verify it opens the original job link.
