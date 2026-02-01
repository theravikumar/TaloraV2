# How to Test with Any Resume

The system works with **any PDF resume**. Here's how to test it:

## Quick Test (Command Line)

```bash
cd /home/ravi/Documents/projects/TaloraV2

# Test with any resume PDF
uv run python scripts/demo_resume_matching.py <path_to_resume.pdf>

# Example with your resume
uv run python scripts/demo_resume_matching.py data/resumes/ravi_resume_9608676321.pdf

# Example with custom job search
uv run python scripts/demo_resume_matching.py data/resumes/john.pdf "data scientist" "Mumbai"
```

## What it Does

1. Extracts text from the PDF resume
2. Uses LLM to parse resume structure (skills, experience, work units)
3. Searches for real jobs on LinkedIn
4. Matches the resume against jobs
5. Shows top matching jobs with scores

## Testing with Different Resumes

### Option 1: Use Existing Resume

```bash
# Your resume
uv run python scripts/demo_resume_matching.py data/resumes/ravi_resume_9608676321.pdf
```

### Option 2: Add New Resume

```bash
# 1. Copy any PDF resume to data/resumes/
cp /path/to/new_resume.pdf data/resumes/

# 2. Run matching
uv run python scripts/demo_resume_matching.py data/resumes/new_resume.pdf
```

### Option 3: Test with Different Job Types

```bash
# Backend developer
uv run python scripts/demo_resume_matching.py data/resumes/resume.pdf "backend engineer python" "Bangalore"

# Data scientist
uv run python scripts/demo_resume_matching.py data/resumes/resume.pdf "data scientist" "India"

# Frontend developer  
uv run python scripts/demo_resume_matching.py data/resumes/resume.pdf "react developer" "Remote"
```

## Python API Usage

You can also use it programmatically:

```python
from match_engine.resume import resume_normalizer
from match_engine.matcher import job_matcher
from job_pipeline.scrapers import linkedin_scraper
from job_pipeline.normalizers import job_normalizer

# 1. Load any resume
resume = resume_normalizer.normalize_from_pdf("path/to/resume.pdf")
print(f"Resume: {resume['name']}")
print(f"Experience: {resume['years_of_experience']} years")

# 2. Get jobs
jobs = linkedin_scraper.scrape_jobs(
    keywords="machine learning",
    location="India",
    limit=10
)

# 3. Normalize jobs
for job in jobs:
    jd_profile = job_normalizer.normalize(job['raw_text'])
    job['jd_profile'] = jd_profile

# 4. Match
matches = job_matcher.match_jobs(resume, jobs, top_n=5)

# 5. View results
for match in matches:
    print(f"{match['job']['job_title']}: {match['score']*100:.0f}% match")
```

## Output

The script outputs:
- Resume summary (name, experience, skills)
- Top matching jobs with scores
- Gaps (missing requirements)
- Saved JSON results in `data/match_results/`

## Example Output

```
==============================================================
RESUME MATCHING DEMO
==============================================================

1. Loading resume from: data/resumes/john_doe.pdf
   Name: John Doe
   Experience: 5 years
   Skills: 15 extracted
   Work Units: 10 extracted

2. Searching for 'python developer' jobs in India...
   Found 10 jobs

3. Normalizing top 5 jobs...
   - Senior Python Developer (8 requirements)
   - Backend Engineer (12 requirements)
   - Full Stack Developer (15 requirements)

4. Matching resume to 5 jobs...

==============================================================
TOP 5 JOB MATCHES
==============================================================

1. Senior Python Developer
   Company: TechCorp
   Location: Bangalore, India
   Match Score: 67%
   Requirements Met: 8/12
   URL: https://linkedin.com/jobs/...

2. Backend Engineer
   Company: StartupXYZ
   Location: Remote
   Match Score: 54%
   Requirements Met: 6/11
   URL: https://linkedin.com/jobs/...
```

## Notes

- Works with **any PDF resume** in any format
- LLM extracts structured data automatically
- Matching is based on:
  - Embedding similarity (semantic matching)
  - Domain overlap (backend, ML, frontend, etc.)
  - Tool/technology matching
  - Proficiency levels

## Limitations

- LinkedIn Guest API doesn't provide full job descriptions
- For better matching, use detailed job postings
- Resume extraction quality depends on PDF format

## Next Steps

For production use:
1. Use detailed job descriptions (from company career pages)
2. Increase job search limit (currently 10 for demo speed)
3. Add more job sources (RemoteOK, ArbeitNow, etc.)
