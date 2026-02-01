# job_pipeline/storage/database.py
"""
SQLite database manager for job storage.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from shared.config import settings
from shared.schema import NormalizedJob


class JobDatabase:
    """
    Manages SQLite database for job metadata.
    Stores all job information except embeddings (those go in FAISS).
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Jobs table (main)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                job_url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                
                -- Company info
                company_name TEXT NOT NULL,
                company_url TEXT,
                
                -- Job basics
                job_title TEXT NOT NULL,
                location TEXT,
                work_mode TEXT,
                employment_type TEXT,
                
                -- Compensation & experience
                salary TEXT,
                experience_level TEXT,
                
                -- Timestamps
                posted_date TEXT,
                scraped_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                
                -- Matching metadata
                domain TEXT,
                extraction_quality REAL DEFAULT 1.0,
                
                -- Status
                is_active INTEGER DEFAULT 1,
                
                -- Raw data (for debugging)
                raw_text TEXT,
                
                -- Normalized profile (JSON)
                jd_profile_json TEXT NOT NULL,
                
                -- Indexes
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for fast lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company ON jobs(company_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON jobs(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_location ON jobs(location)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_active ON jobs(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posted_date ON jobs(posted_date)")
        
        conn.commit()
        conn.close()
        
        print(f"[OK] Database initialized: {self.db_path}")
    
    def insert_job(self, job: Dict) -> bool:
        """
        Insert or update a job.
        
        Args:
            job: NormalizedJob dictionary
            
        Returns:
            True if inserted, False if duplicate (job_url exists)
        """
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO jobs (
                    job_id, job_url, source, company_name, company_url,
                    job_title, location, work_mode, employment_type,
                    salary, experience_level, posted_date, scraped_at,
                    last_updated, domain, extraction_quality, is_active,
                    raw_text, jd_profile_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job['job_id'],
                job['job_url'],
                job['source'],
                job['company_name'],
                job.get('company_url'),
                job['job_title'],
                job.get('location'),
                job.get('work_mode'),
                job.get('employment_type'),
                job.get('salary'),
                job.get('experience_level'),
                job.get('posted_date'),
                job['scraped_at'],
                job['last_updated'],
                job.get('domain'),
                job.get('extraction_quality', 1.0),
                1 if job.get('is_active', True) else 0,
                job.get('raw_text'),
                json.dumps(job['jd_profile'])
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            # Duplicate job_url
            conn.close()
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        import json
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        job = dict(row)
        job['jd_profile'] = json.loads(job['jd_profile_json'])
        del job['jd_profile_json']
        job['is_active'] = bool(job['is_active'])
        
        return job
    
    def get_all_active_jobs(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all active jobs"""
        import json
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM jobs WHERE is_active = 1 ORDER BY posted_date DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            job = dict(row)
            job['jd_profile'] = json.loads(job['jd_profile_json'])
            del job['jd_profile_json']
            job['is_active'] = bool(job['is_active'])
            jobs.append(job)
        
        return jobs
    
    def count_jobs(self, active_only: bool = True) -> int:
        """Count total jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1")
        else:
            cursor.execute("SELECT COUNT(*) FROM jobs")
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def search_jobs(self, filters: Dict) -> List[Dict]:
        """
        Search jobs with filters.
        
        Args:
            filters: Dictionary of filter criteria
                - domains: List[str]
                - locations: List[str]
                - companies: List[str]
                - min_extraction_quality: float
        """
        import json
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM jobs WHERE is_active = 1"
        params = []
        
        # Domain filter
        if filters.get('domains'):
            placeholders = ','.join('?' * len(filters['domains']))
            query += f" AND domain IN ({placeholders})"
            params.extend(filters['domains'])
        
        # Location filter
        if filters.get('locations'):
            placeholders = ','.join('?' * len(filters['locations']))
            query += f" AND location IN ({placeholders})"
            params.extend(filters['locations'])
        
        # Company filter
        if filters.get('companies'):
            placeholders = ','.join('?' * len(filters['companies']))
            query += f" AND company_name IN ({placeholders})"
            params.extend(filters['companies'])
        
        # Quality filter
        if filters.get('min_extraction_quality'):
            query += " AND extraction_quality >= ?"
            params.append(filters['min_extraction_quality'])
        
        query += " ORDER BY posted_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            job = dict(row)
            job['jd_profile'] = json.loads(job['jd_profile_json'])
            del job['jd_profile_json']
            job['is_active'] = bool(job['is_active'])
            jobs.append(job)
        
        return jobs


# Singleton
job_database = JobDatabase()
