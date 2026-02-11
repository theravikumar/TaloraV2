# Talora - AI-Powered Job Matching Platform

Empowering talent to grow. AI-powered platform that helps you understand your skills, find jobs that truly fit, and grow your career over time.

## What Talora Does

**Find the right opportunities**
- Jobs ranked by real fit, not just keywords
- Understand exactly which requirements you meet
- See your strengths and gaps clearly

**Improve continuously**
- Get insights to strengthen your resume
- Know where you stand in the market
- Focus on relevant opportunities, skip the noise

**Works for everyone**
- Backend, Frontend, ML, DevOps, Design, Product - all domains
- Junior to senior levels
- Technical and non-technical roles

## Quick Start

### 1. Prerequisites

- Python 3.11+
- **uv** (recommended) OR **pip**

### 2. Installation

**Option A: Using uv (Recommended)**
```bash
# Clone repository
git clone https://github.com/theravikumar/TaloraV2.git
cd TaloraV2

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

**Option B: Using pip**
```bash
# Clone repository
git clone https://github.com/theravikumar/TaloraV2.git
cd TaloraV2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys (Groq is required, free tier available)
```

### 3. Run a Demo

```bash
# Match any resume to jobs
uv run python scripts/demo_resume_matching.py data/resumes/your_resume.pdf
```

## Key Features

### Intelligent Matching (Not Just Keywords)
- Understands context: "built RAG systems" matches "LLM application development"
- Domain-aware: distinguishes ML engineering from data science
- Proficiency-based: matches junior vs senior requirements accurately

### Comprehensive Job Coverage
- Resume parsing with LLM (Groq/Gemini)
- Semantic matching using embeddings
- Domain/skill/proficiency aware scoring
- Gap analysis for missing requirements

### Production Ready
- SQLite database for job storage
- FAISS vector store for fast similarity search
- Modular architecture for easy scaling

## Technology Stack

- **LLMs**: Groq (primary), Gemini (fallback), Ollama (offline)
- **Embeddings**: sentence-transformers (all-mpnet-base-v2)
- **Database**: SQLite (development), PostgreSQL (production planned)
- **Vector Store**: FAISS
- **Job Sources**: LinkedIn Guest API, RemoteOK, ArbeitNow

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
