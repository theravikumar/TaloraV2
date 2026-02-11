#!/usr/bin/env python
"""
Seed job database with test data
"""
import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from job_pipeline.storage.database import JobDatabase
from job_pipeline.normalizers.job_normalizer import JobNormalizer

def main():
    print("=" * 60)
    print("SEEDING JOB DATABASE")
    print("=" * 60)
    
    # Initialize
    job_db = JobDatabase()
    normalizer = JobNormalizer()
    
    # Load test jobs
    test_file = Path(__file__).parent.parent / "data" / "ml_test_jobs.json"
    
    print(f"\n1. Loading jobs from {test_file.name}...")
    with open(test_file) as f:
        jobs = json.load(f)
    
    print(f"   Found {len(jobs)} jobs")
    
    # Normalize and store
    print("\n2. Normalizing and storing jobs...")
    stored_count = 0
    
    for i, job in enumerate(jobs[:10], 1):  # Limit to 10 for speed
        try:
            print(f"   [{i}/10] {job.get('job_title', 'Unknown')[:50]}...", end=" ")
            
            # Normalize
            jd_profile = normalizer.normalize(job.get('raw_text', ''))
            
            # Store
            job_db.insert_job({
                **job,
                'jd_profile': jd_profile
            })
            
            stored_count += 1
            print("OK")
            
        except Exception as e:
            print(f"FAILED: {e}")
    
    print(f"\n3. Successfully stored {stored_count} jobs")
    
    # Verify
    print("\n4. Verifying database...")
    all_jobs = job_db.search_jobs(limit=100)
    print(f"   Total jobs in database: {len(all_jobs)}")
    
    if all_jobs:
        print(f"\n5. Sample job:")
        sample = all_jobs[0]
        print(f"   Title: {sample.get('job_title')}")
        print(f"   Company: {sample.get('company_name')}")
        print(f"   Location: {sample.get('location')}")
        print(f"   Has JD Profile: {'Yes' if sample.get('jd_profile') else 'No'}")
    
    print("\n" + "=" * 60)
    print("DATABASE SEEDING COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
