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

- Python 3.10+
- uv package manager

### 2. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd TaloraV2

# Install dependencies
uv sync

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

## Project Structure

```
TaloraV2/
├── job_pipeline/          # Job scraping and normalization
│   ├── scrapers/          # LinkedIn, RemoteOK, ArbeitNow
│   ├── normalizers/       # LLM-based job parsing
│   └── storage/           # Database and embeddings
├── match_engine/          # Resume matching logic
│   ├── resume/            # Resume parsing
│   └── matcher/           # Matching algorithms
├── shared/                # Common utilities
│   ├── llm/               # LLM clients (Groq, Gemini, Ollama)
│   ├── embeddings/        # Sentence transformers
│   └── schema/            # Data models
├── scripts/               # Utility scripts
└── data/                  # Local data storage
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and code flow
- [DEVELOPMENT.md](DEVELOPMENT.md) - How to run, test, and develop
- [HOW_TO_TEST.md](HOW_TO_TEST.md) - Testing with different resumes

## Technology Stack

- **LLMs**: Groq (primary), Gemini (fallback), Ollama (offline)
- **Embeddings**: sentence-transformers (all-mpnet-base-v2)
- **Database**: SQLite (development), PostgreSQL (production planned)
- **Vector Store**: FAISS
- **Job Sources**: LinkedIn Guest API, RemoteOK, ArbeitNow

## Current Status

- Batch 1: Foundation - COMPLETE
- Batch 2: Job Pipeline - COMPLETE  
- Batch 3: Matching Engine - COMPLETE
- Batch 4: Production API - PLANNED

## Team

Lead: Ravi Kumar (ML Engineer, 3.5 years)
- LinkedIn scraping & free API integration
- Resume parsing with LLMs
- Semantic matching algorithm

## License

MIT License (or your preferred license)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
