#!/usr/bin/env python3
"""
RemoteOK Scraper with AI Description Generation
"""

import sys
import os
import sqlite3
import json
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))
print(f"Project root added to path: {PROJECT_ROOT}")

from job_pipeline.scrapers.remoteok_scraper import remoteok_scraper
from shared.llm.router import llm_router
from unified_run_scrapers import save_job_metadata, clean_job_role_llm, save_work_units, DB_PATH
from job_pipeline.normalizers.job_normalizer import job_normalizer

def generate_clean_description(job_title, company, raw_text):
    """
    Use LLM to generate a clean, professional job description.
    """
    prompt = f"""
    You are a professional HR assistant. 
    
    Task: Create a clean, professional job description based ONLY on the provided information.
    
    Rules:
    1. If the 'Raw Text' contains a full description, clean it up (remove HTML, remove spam like "Please mention...", fix formatting).
    2. If the 'Raw Text' is missing or very short (e.g. just title/tags), generate a 2-3 sentence professional summary stating that {company} is hiring a {job_title} with the listed skills.
    3. CRITICAL: DO NOT add any new requirements, years of experience, or duties that are not explicitly present in the input. Do not hallucinate.
    4. Structure the output clearly (e.g. About the Role, Requirements).
    
    Job Title: {job_title}
    Company: {company}
    Raw Text:
    {raw_text[:3000]}
    
    Clean Job Description:
    """
    
    try:
        response = llm_router.complete(
            prompt=prompt,
            use_case="job_description_generation",
            temperature=0.2, # Lower temperature to reduce hallucination
            max_tokens=1000
        )
        return response.strip()
    except Exception as e:
        print(f"   [!] LLM generation failed: {e}")
        return raw_text  # Fallback to raw text

def run_scraper():
    print("=" * 60)
    print("REMOTEOK SCRAPER - WORLDWIDE - AI POWERED")
    print("=" * 60)
    
    # 1. Fetch filtered jobs
    print("\n[1/3] Fetching jobs from RemoteOK (Worldwide)...")
    jobs = remoteok_scraper.scrape_all_jobs(limit=1000) # Removed location="India"
    
    if not jobs:
        print("No jobs found matching criteria.")
        return
        
    print(f"      Found {len(jobs)} potential jobs.")
    
    # 2. Process and Save
    print("\n[2/3] Generating descriptions and saving...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    success_count = 0
    
    for i, job in enumerate(jobs, 1):
        try:
            print(f"      ({i}/{len(jobs)}) Processing: {job['job_title'][:30]}...", end=" ", flush=True)
            
            # Generate Clean Description
            raw_text = job.get('raw_text', '')
            clean_desc = generate_clean_description(
                job['job_title'], 
                job['company_name'], 
                raw_text
            )
            
            # Update job object
            job['job_description'] = clean_desc
            # Keep raw_text as backup but clean desc is primary
            
            # Clean Role
            cleaned_role = clean_job_role_llm(job['job_title'], job['company_name'])
            
            # Normalize for Work Units (using the NEW clean description)
            jd_profile = job_normalizer.normalize(clean_desc)
            
            # Save Metadata
            job_id = save_job_metadata(cursor, job, cleaned_role)
            
            # Save Work Units
            save_work_units(cursor, job_id, jd_profile)
            
            success_count += 1
            print(f"[OK]")
            
            # Rate limit LLM
            time.sleep(1.5)
            
        except Exception as e:
            print(f"[FAILED: {e}]")
            continue
            
    conn.commit()
    conn.close()
    
    print("\n[3/3] Process Complete!")
    print(f"      Successfully saved {success_count} jobs with AI-generated descriptions.")
    print("=" * 60)

if __name__ == "__main__":
    run_scraper()
