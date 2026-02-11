# api/services/job_service.py
"""
Job search service - Fixed to match actual DB schema
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from api.config import get_settings

settings = get_settings()


class JobService:
    """Service for job search and retrieval"""
    
    def __init__(self):
        # Use existing jobs database
        self.db_path = settings.db_path if hasattr(settings, 'db_path') else "./data/jobs.db"
    
    def search_jobs(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search jobs from existing database.
        
        Returns paginated job results.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM jobs WHERE is_active = 1"
        params = []
        
        if keywords:
            query += " AND (job_title LIKE ? OR company_name LIKE ?)"
            params.extend([f"%{keywords}%", f"%{keywords}%"])
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        query += f" ORDER BY posted_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            # Parse JD profile to get requirements count
            try:
                jd_profile = json.loads(row["jd_profile_json"]) if row["jd_profile_json"] else {}
                work_units = jd_profile.get("work_units", [])
                req_count = len(work_units)
            except (json.JSONDecodeError, KeyError):
                req_count = 0
            
            jobs.append({
                "job_id": row["job_id"],
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "location": row["location"],
                "domain": row["domain"],
                "posted_date": row["posted_date"],
                "salary": row["salary"] if "salary" in row.keys() else None,
                "work_mode": row["work_mode"] if "work_mode" in row.keys() else None,
                "requirements_count": req_count
            })
        
        conn.close()
        
        return {
            "total": total,
            "jobs": jobs
        }
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Parse JD profile
        try:
            jd_profile = json.loads(row["jd_profile_json"]) if row["jd_profile_json"] else {}
        except json.JSONDecodeError:
            jd_profile = {}
        
        return {
            "job_id": row["job_id"],
            "job_title": row["job_title"],
            "company_name": row["company_name"],
            "location": row["location"],
            "domain": row["domain"],
            "posted_date": row["posted_date"],
            "salary": row["salary"] if "salary" in row.keys() else None,
            "work_mode": row["work_mode"] if "work_mode" in row.keys() else None,
            "employment_type": row["employment_type"] if "employment_type" in row.keys() else None,
            "experience_level": row["experience_level"] if "experience_level" in row.keys() else None,
            "raw_text": row["raw_text"] if "raw_text" in row.keys() else None,
            "jd_profile": jd_profile,
            "work_units": jd_profile.get("work_units", []),
            "requirements_count": len(jd_profile.get("work_units", []))
        }
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs for matching"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE is_active = 1")
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            # Parse JD profile
            try:
                jd_profile = json.loads(row[" jd_profile_json"]) if row["jd_profile_json"] else {}
            except (json.JSONDecodeError, KeyError):
                jd_profile = {}
            
            jobs.append({
                "id": row["job_id"],
                "job_id": row["job_id"],
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "location": row["location"],
                "domain": row["domain"],
                "jd_profile": jd_profile
            })
        
        return jobs
