#!/usr/bin/env python3
"""
Unified Scraping & Storage Script
Scrapes jobs from all sources, cleans job roles, extracts work units,
and saves to the dual-table database (jobs and job_work_units).
"""

import sys
import os
import sqlite3
import json
import uuid
import re
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from job_pipeline.scrapers.multi_source_scraper import multi_source_scraper
from job_pipeline.normalizers.job_normalizer import job_normalizer
from shared.llm.router import llm_router
from shared.config import settings

DB_PATH = PROJECT_ROOT / "data" / "jobs.db"

def clean_job_role_llm(job_title, company_name):
    """
    Use LLM to extract a clean Job Role from a messy title.
    Example: "Sales – Account Executive DroneSense" -> "Account Executive"
    """
    prompt = f"""
    Extract ONLY the professional job role from the following job title and company.
    Remove company names, locations, department prefixes, and extraneous noise.
    If the title contains multiple roles, pick the most senior or primary one.
    Return ONLY the job role name, no other text.

    Job Title: {job_title}
    Company: {company_name}

    Clean Job Role:
    """
    try:
        role = llm_router.complete(
            prompt=prompt,
            use_case="job_extraction",
            temperature=0,
            max_tokens=50
        ).strip().strip('"').strip("'")
        
        # Simple local cleanup for safety
        role = re.sub(rf"(?i)\s*{re.escape(company_name)}\s*", "", role)
        return role
    except Exception as e:
        print(f"   [!] LLM role extraction failed for '{job_title}': {e}")
        # Fallback to simple regex if LLM fails
        return re.sub(rf"(?i)\s*{re.escape(company_name)}\s*", "", job_title).split('-')[0].split('|')[0].strip()

def save_job_metadata(cursor, job_data, cleaned_role, extraction_quality=1.0):
    """Save high-level metadata to the jobs table"""
    job_id = job_data.get("job_id") or str(uuid.uuid4())
    
    query = """
    INSERT OR REPLACE INTO jobs (
        job_id, job_url, source, company_name, company_url,
        job_title, job_role, location, work_mode, employment_type,
        salary_raw, experience_raw, domain, posted_date, 
        scraped_at, last_updated, extraction_quality, is_active,
        raw_text, job_description
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, 1, ?, ?);
    """
    
    params = (
        job_id,
        job_data.get("job_url"),
        job_data.get("source", "unknown"),
        job_data.get("company_name"),
        job_data.get("company_url"),
        job_data.get("job_title"),
        cleaned_role,
        job_data.get("location"),
        job_data.get("work_mode"),
        job_data.get("employment_type"),
        job_data.get("salary"),
        job_data.get("experience_level"),
        job_data.get("domain", "General"),
        job_data.get("posted_date"),
        extraction_quality,
        job_data.get("raw_text") or job_data.get("job_description"),
        job_data.get("job_description")
    )
    
    cursor.execute(query, params)
    return job_id

def save_work_units(cursor, job_id, jd_profile):
    """Save individual work units to the job_work_units table"""
    # Delete existing units if any (for updates)
    cursor.execute("DELETE FROM job_work_units WHERE job_id = ?", (job_id,))
    
    # Process required and preferred expectations
    for priority in ["required_expectations", "preferred_expectations"]:
        short_priority = "required" if "required" in priority else "preferred"
        for exp_idx, expectation in enumerate(jd_profile.get(priority, [])):
            for wu_idx, wu in enumerate(expectation.get("work_units", [])):
                vector_id = f"{job_id}:{short_priority[:3]}:{exp_idx}:{wu_idx}"
                
                query = """
                INSERT INTO job_work_units (
                    job_id, priority, action, object, tools, constraints, outcome, vector_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """
                
                params = (
                    job_id,
                    short_priority,
                    wu.get("action"),
                    wu.get("object"),
                    json.dumps(wu.get("tools", [])),
                    json.dumps(wu.get("constraints", [])),
                    wu.get("outcome"),
                    vector_id
                )
                cursor.execute(query, params)

def run_unified_pipeline():
    print("=" * 60)
    print("UNIFIED SCRAPING & WORK UNIT PIPELINE")
    print("=" * 60)

    # 1. Scrape
    print("\n[1/3] Collecting jobs from all sources...")
    # For speed in this demo, limit to a small number or specific sources if needed
    # raw_jobs = multi_source_scraper.get_daily_jobs()
    
    # To ensure we get diverse results but not thousands for the first run:
    raw_jobs = multi_source_scraper.scrape_and_merge(limit_per_source=10)
    print(f"      Total unique jobs collected: {len(raw_jobs)}")

    # 2. Process and Store
    print("\n[2/3] Processing and storing jobs...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    success_count = 0
    for i, job in enumerate(raw_jobs, 1):
        try:
            print(f"      ({i}/{len(raw_jobs)}) Processing: {job['job_title'][:40]}...", end=" ")
            
            # Clean Role
            cleaned_role = clean_job_role_llm(job['job_title'], job['company_name'])
            
            # Normalize for Work Units
            jd_text = job.get("job_description") or job.get("raw_text") or job.get("job_title")
            jd_profile = job_normalizer.normalize(jd_text)
            
            # Save Metadata
            job_id = save_job_metadata(cursor, job, cleaned_role)
            
            # Save Work Units
            save_work_units(cursor, job_id, jd_profile)
            
            success_count += 1
            print(f"[Role: {cleaned_role}] [OK]")
            
        except Exception as e:
            print(f"[FAILED: {e}]")
            continue
            
    conn.commit()
    conn.close()
    
    print("\n[3/3] Collection Complete!")
    print(f"      Successfully saved {success_count} jobs with Work Units.")
    print("=" * 60)

if __name__ == "__main__":
    run_unified_pipeline()
