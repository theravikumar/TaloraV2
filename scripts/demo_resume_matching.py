#!/usr/bin/env python3
"""
Demo: Match Any Resume to Jobs

Usage:
    python scripts/demo_resume_matching.py <path_to_resume.pdf>

Example:
    python scripts/demo_resume_matching.py data/resumes/john_resume.pdf
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from match_engine.resume import resume_normalizer
from match_engine.matcher import job_matcher
from job_pipeline.normalizers import job_normalizer
from job_pipeline.scrapers import linkedin_scraper


def match_resume_to_jobs(resume_pdf_path: str, keywords: str = "software engineer", location: str = "India"):
    """
    Match any resume PDF to real jobs.
    
    Args:
        resume_pdf_path: Path to PDF resume
        keywords: Job search keywords
        location: Job location to search
    """
    
    print("=" * 60)
    print("RESUME MATCHING DEMO")
    print("=" * 60)
    
    # 1. Normalize resume
    print(f"\n1. Loading resume from: {resume_pdf_path}")
    try:
        resume = resume_normalizer.normalize_from_pdf(resume_pdf_path)
        print(f"   Name: {resume.get('name', 'Unknown')}")
        print(f"   Experience: {resume.get('years_of_experience', 0)} years")
        print(f"   Skills: {len(resume.get('skills', []))} extracted")
        print(f"   Work Units: {len(resume.get('work_units', []))} extracted")
    except Exception as e:
        print(f"   Error loading resume: {e}")
        return
    
    # 2. Get real jobs from LinkedIn
    print(f"\n2. Searching for '{keywords}' jobs in {location}...")
    raw_jobs = linkedin_scraper.scrape_jobs(
        keywords=keywords,
        location=location,
        limit=10
    )
    print(f"   Found {len(raw_jobs)} jobs")
    
    if not raw_jobs:
        print("   No jobs found. Try different keywords.")
        return
    
    # 3. Normalize first 5 jobs (quick demo)
    print(f"\n3. Normalizing top {min(5, len(raw_jobs))} jobs...")
    jobs = []
    for job in raw_jobs[:5]:
        try:
            # Use job title as description (LinkedIn guest API doesn't have full descriptions)
            jd_text = f"{job['job_title']} at {job['company_name']} in {job['location']}"
            jd_profile = job_normalizer.normalize(jd_text)
            
            # Flatten work units
            all_work_units = []
            for exp in jd_profile.get('required_expectations', []):
                all_work_units.extend(exp.get('work_units', []))
            for exp in jd_profile.get('preferred_expectations', []):
                all_work_units.extend(exp.get('work_units', []))
            
            jd_profile['work_units'] = all_work_units
            job['jd_profile'] = jd_profile
            jobs.append(job)
            print(f"   - {job['job_title']} ({len(all_work_units)} requirements)")
        except Exception as e:
            print(f"   Error normalizing {job.get('job_title', 'job')}: {e}")
    
    if not jobs:
        print("   No jobs could be normalized.")
        return
    
    # 4. Match
    print(f"\n4. Matching resume to {len(jobs)} jobs...")
    matches = job_matcher.match_jobs(resume, jobs, top_n=10)
    
    # 5. Display results
    print(f"\n{'=' * 60}")
    print(f"TOP {len(matches)} JOB MATCHES")
    print("=" * 60)
    
    for i, match in enumerate(matches, 1):
        job = match['job']
        score_pct = match['score'] * 100
        
        print(f"\n{i}. {job['job_title']}")
        print(f"   Company: {job['company_name']}")
        print(f"   Location: {job['location']}")
        print(f"   Match Score: {score_pct:.0f}%")
        print(f"   Requirements Met: {match['matched_count']}/{match['total_requirements']}")
        print(f"   URL: {job['job_url']}")
        
        if match['gaps'] and len(match['gaps']) > 0:
            print(f"   Gaps: {len(match['gaps'])} requirements not fully met")
    
    # 6. Save results
    output_dir = Path("data/match_results")
    output_dir.mkdir(exist_ok=True)
    
    resume_name = Path(resume_pdf_path).stem
    output_file = output_dir / f"{resume_name}_matches.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'resume': resume,
            'matches': matches
        }, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/demo_resume_matching.py <resume.pdf> [keywords] [location]")
        print("\nExample:")
        print("  python scripts/demo_resume_matching.py data/resumes/ravi_resume.pdf")
        print("  python scripts/demo_resume_matching.py data/resumes/john.pdf 'data scientist' 'Mumbai'")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    keywords = sys.argv[2] if len(sys.argv) > 2 else "software engineer"
    location = sys.argv[3] if len(sys.argv) > 3 else "India"
    
    match_resume_to_jobs(resume_path, keywords, location)
