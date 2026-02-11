# Development Guide

## Setup

### 1. Install uv

```bash
# If not installed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Install

```bash
git clone <repo-url>
cd TaloraV2
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add:
```bash
# Required (free tier available)
GROQ_API_KEY=your_groq_key_here

# Optional (free tier)
GEMINI_API_KEY=your_gemini_key_here

# Optional (local, no key needed)
OLLAMA_BASE_URL=http://localhost:11434
```

**Get Free API Keys**:
- Groq: https://console.groq.com (free 30 req/min)
- Gemini: https://ai.google.dev (free 15 req/min)

## Running the System

### Test Resume Matching

```bash
# Basic test
uv run python scripts/demo_resume_matching.py data/resumes/ravi_resume_9608676321.pdf

# Custom job search
uv run python scripts/demo_resume_matching.py data/resumes/resume.pdf "python developer" "Bangalore"
```

### Collect Jobs Daily

```bash
# Get jobs from all sources
uv run python -c "
from job_pipeline.scrapers import multi_source_scraper

jobs = multi_source_scraper.scrape_and_merge(
    limit_per_source=300,
    deduplicate=True
)

print(f'Collected {len(jobs)} jobs')
"
```

### Test Individual Components

**Test LLM Connection**:
```bash
uv run python -c "from shared.llm import llm_router; llm_router.test_all()"
```

**Test Job Scraping**:
```bash
uv run python -c "
from job_pipeline.scrapers import linkedin_scraper

jobs = linkedin_scraper.scrape_jobs('ML engineer', 'India', 10)
print(f'Found {len(jobs)} jobs')
for job in jobs[:3]:
    print(f'- {job[\"job_title\"]} at {job[\"company_name\"]}')
"
```

**Test Resume Parsing**:
```bash
uv run python -c "
from match_engine.resume import resume_normalizer

resume = resume_normalizer.normalize_from_pdf('data/resumes/ravi_resume_9608676321.pdf')
print(f'Name: {resume[\"name\"]}')
print(f'Experience: {resume[\"years_of_experience\"]} years')
print(f'Work units: {len(resume[\"work_units\"])}')
"
```

## Project Structure Explained

### job_pipeline/

**scrapers/** - Collect jobs from free sources
- `linkedin_scraper.py` - LinkedIn Guest API (no auth)
- `remoteok_scraper.py` - RemoteOK public API
- `arbeitnow_scraper.py` - ArbeitNow API
- `multi_source_scraper.py` - Combines all sources

**normalizers/** - Parse job descriptions
- `job_normalizer.py` - Uses LLM to extract requirements
- `prompts.py` - LLM prompts for extraction

**storage/** - Store jobs and embeddings
- `database.py` - SQLite for job metadata
- `embedding_store.py` - FAISS for vector search

### match_engine/

**resume/** - Parse resumes
- `resume_normalizer.py` - PDF → structured data

**matcher/** - Match resumes to jobs
- `work_unit_matcher.py` - Compare individual requirements
- `job_matcher.py` - Rank all jobs by score

### shared/

**llm/** - LLM clients
- `groq_client.py` - Groq (primary, fast)
- `gemini_client.py` - Gemini (fallback)
- `ollama_client.py` - Ollama (offline)
- `router.py` - Smart routing with fallback

**embeddings/** - Vector embeddings
- `generator.py` - Sentence transformers (768D)

**schema/** - Data models
- `base.py` - WorkUnit, JobProfile, ResumeProfile

## Common Tasks

### Add New Job Source

1. Create scraper in `job_pipeline/scrapers/`
2. Follow the pattern:
```python
class NewSourceScraper:
    def scrape_jobs(self, **kwargs) -> List[Dict]:
        # Return list of jobs in standard format
        return [{
            'job_id': '...',
            'job_title': '...',
            'company_name': '...',
            'location': '...',
            'raw_text': '...',
            # ... other fields
        }]
```
3. Add to `multi_source_scraper.py`

### Add New Matching Feature

Modify `match_engine/matcher/work_unit_matcher.py`:
```python
def match_units(self, resume_unit, job_unit):
    # Existing: embedding similarity, domain bonus, tool bonus
    
    # Add your bonus here
    your_bonus = self._calculate_your_bonus(resume_unit, job_unit)
    
    final_score = similarity + domain_bonus + your_bonus
    return final_score
```

### Change LLM Model

Edit `.env`:
```bash
# For Groq
GROQ_MODEL=llama-3.1-70b-versatile

# For Gemini  
GEMINI_MODEL=gemini-2.0-flash
```

## Testing

### Run All Tests

```bash
uv run pytest tests/
```

### Test Specific Component

```bash
uv run pytest tests/test_job_normalizer.py
```

### Manual Integration Test

```bash
# Full pipeline test
uv run python -c "
from job_pipeline.scrapers import linkedin_scraper
from job_pipeline.normalizers import job_normalizer
from match_engine.resume import resume_normalizer
from match_engine.matcher import job_matcher

# 1. Get jobs
jobs = linkedin_scraper.scrape_jobs('software engineer', 'India', 5)

# 2. Normalize jobs
for job in jobs:
    jd = job_normalizer.normalize(job['raw_text'])
    job['jd_profile'] = jd

# 3. Parse resume
resume = resume_normalizer.normalize_from_pdf('data/resumes/ravi_resume_9608676321.pdf')

# 4. Match
matches = job_matcher.match_jobs(resume, jobs)

print(f'Top match: {matches[0][\"job\"][\"job_title\"]} ({matches[0][\"score\"]*100:.0f}%)')
"
```

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check LLM Responses

```python
response = llm_router.complete("test prompt", use_case="job_extraction")
print(response)  # See raw LLM output
```

### Inspect Embeddings

```python
from shared.embeddings import embedding_generator

text = "Python developer with ML experience"
emb = embedding_generator.embed(text)
print(f"Embedding shape: {emb.shape}")  # Should be (768,)
```

## Performance Tips

1. **Batch embeddings**: Use `embed_batch()` not `embed()` in loops
2. **Cache resume parsing**: Don't re-parse same resume
3. **Limit job normalization**: Expensive LLM call, normalize only when needed
4. **Use FAISS**: Don't scan all jobs linearly

## Troubleshooting

**Import errors**:
```bash
uv sync  # Reinstall dependencies
```

**LLM quota exceeded**:
- Groq: Wait 1 minute (rate limit resets)
- Gemini: Wait or use Ollama (offline)

**PDF extraction fails**:
- Ensure PDF is text-based (not scanned image)
- Try different PDF library if needed

**No jobs found**:
- Check internet connection
- Try different keywords
- LinkedIn API may be temporarily down

## Code Style

- Use type hints
- Document functions with docstrings
- Keep functions under 50 lines
- Use meaningful variable names
- No emojis in production code

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: description"

# Push and create PR
git push origin feature/your-feature
```

## Need Help?

- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check [HOW_TO_TEST.md](HOW_TO_TEST.md) for testing guides
- Ask team lead (Ravi)
