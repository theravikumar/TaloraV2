
import sys
import os
import sqlite3
import json
import uuid
import re
from datetime import datetime

# Ensure we can import from the project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_pipeline.scrapers.multi_source_scraper import multi_source_scraper

DB_PATH = "./data/jobs.db"

def clean_title(title: str) -> str:
    """Clean job title by removing gender markers and extra info"""
    if not title:
        return "Unknown"
    
    # Remove (m/w/d), (f/m/x), etc.
    # Case insensitive
    title = re.sub(r'(?i)\s*\(m/w/d\)\s*', '', title)
    title = re.sub(r'(?i)\s*\([mKwWfFdDxX/]+\)\s*', '', title)
    title = re.sub(r'\s*\[.*?\]\s*', '', title)
    
    return title.strip()

def extract_jd_profile(text: str, title: str) -> str:
    """Extract simple profile from text for semantic search"""
    if not text:
        return json.dumps({"work_units": [], "skills": []})
        
    text_lower = text.lower()
    title_lower = title.lower()
    
    # Common tech skills to look for
    common_skills = [
        "python", "javascript", "typescript", "react", "node", "java", "c++", "c#", "go", "rust",
        "aws", "azure", "gcp", "docker", "kubernetes", "sql", "nosql", "mongodb", "postgresql",
        "redis", "kafka", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "html", "css",
        "git", "linux", "agile", "scrum", "jira", "ci/cd", "jenkins", "terraform", "ansible"
    ]
    
    found_skills = [skill for skill in common_skills if skill in text_lower]
    
    # Debug print
    if len(found_skills) > 0:
        print(f"DEBUG: Found skills: {found_skills[:3]}... in {title[:30]}")
    else:
        # Fallback: check title for skills if description failed
        found_skills = [skill for skill in common_skills if skill in title_lower]
        if found_skills:
            print(f"DEBUG: Found skills in TITLE: {found_skills[:3]}")
    
    # Create work units for each skill

    work_units = []
    for skill in found_skills:
        work_units.append({
            "type": "requirement",
            "action": "Utilize",
            "object": "software development technologies",
            "tools": [skill],
            "proficiency": "intermediate",
            "domain": "engineering"
        })
        
    # Add generic role-based units
    if "backend" in title_lower:
        work_units.append({
            "type": "requirement",
            "action": "Develop",
            "object": "backend services",
            "tools": ["API", "Database"],
            "domain": "backend"
        })
    if "frontend" in title_lower:
        work_units.append({
            "type": "requirement",
            "action": "Build",
            "object": "user interfaces",
            "tools": ["UI", "Framework"],
            "domain": "frontend"
        })
        
    return json.dumps({"work_units": work_units, "skills": found_skills})

def save_jobs_to_db(jobs):
    print(f"Saving {len(jobs)} jobs to database: {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        job_title TEXT,
        company_name TEXT,
        location TEXT,
        salary TEXT,
        experience_level TEXT,
        posted_date TEXT,
        scraped_at TEXT NOT NULL,
        last_updated TEXT NOT NULL,
        domain TEXT,
        extraction_quality REAL DEFAULT 1.0,
        is_active INTEGER DEFAULT 1,
        raw_text TEXT,
        jd_profile_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        job_url TEXT,
        job_description TEXT,
        source TEXT NOT NULL DEFAULT 'unknown'
    );
    """)
    
    saved_count = 0
    for job_data in jobs:
        try:
            job_id = job_data.get("job_id") or str(uuid.uuid4())
            
            # Extract description with fallback to raw_text
            description = (
                job_data.get("job_description") or 
                job_data.get("description") or 
                job_data.get("raw_text") or 
                ""
            )

            # Check if job exists
            cursor.execute("SELECT job_description, jd_profile_json FROM jobs WHERE job_id = ?", (job_id,))
            existing = cursor.fetchone()
            
            # If job exists, check if we need to update it
            if existing:
                existing_desc, existing_profile = existing
                
                # Check if profile is empty/placeholder
                try:
                    profile_data = json.loads(existing_profile)
                    has_units = len(profile_data.get("work_units", [])) > 0
                except:
                    has_units = False
                    
                if existing_desc and len(existing_desc) > 10 and has_units:
                    continue # Valid job exists
                else:
                    # print(f"Updating job {job_id} to improve data quality...")
                    cursor.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))

            # Process new/updated job
            cleaned_title = clean_title(job_data.get("job_title"))
            jd_profile = extract_jd_profile(description, cleaned_title)

            query = """
                INSERT INTO jobs (
                    job_id, job_title, company_name, location, 
                    job_url, job_description, posted_date, 
                    is_active, scraped_at, last_updated, 
                    jd_profile_json, domain, salary, experience_level,
                    source
                ) VALUES (
                    ?, ?, ?, ?, 
                    ?, ?, ?, 
                    1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 
                    ?, ?, ?, ?, ?
                )
            """
            
            # Normalize keys
            params = (
                job_id,
                cleaned_title,
                job_data.get("company_name"),
                job_data.get("location"),
                job_data.get("job_url") or job_data.get("url") or f"https://example.com/jobs/{job_id}", # Fallback
                description,
                job_data.get("posted_date"),
                jd_profile,
                job_data.get("domain", "General"),
                job_data.get("salary"),
                job_data.get("experience_level"),
                job_data.get("source", "unknown")
            )
            
            cursor.execute(query, params)
            saved_count += 1
            
        except Exception as e:
            print(f"Error saving job {job_data.get('job_title')}: {e}")
            continue
    
    conn.commit()
    conn.close()
    print(f"Database save complete. Saved {saved_count} new/updated jobs.")

def run_scrapers():
    print("Starting Multi-Source Scraper...")
    try:
        jobs = multi_source_scraper.get_daily_jobs()
        print(f"Scraping complete. Found {len(jobs)} unique jobs.")
        save_jobs_to_db(jobs)
    except Exception as e:
        print(f"Scraping failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_scrapers()
