# api/services/job_service.py
"""
Job search service
"""
import sqlite3
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
        query = "SELECT * FROM jobs WHERE 1=1"
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
        query += f" LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            jobs.append({
                "job_id": row["id"],
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "location": row["location"],
                "domain": row.get("domain"),
                "requirements_count": len(eval(row["requirements"])) if row.get("requirements") else 0
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
        
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "job_id": row["id"],
            "job_title": row["job_title"],
            "company_name": row["company_name"],
            "location": row["location"],
            "domain": row.get("domain"),
            "description": row.get("description"),
            "requirements": eval(row["requirements"]) if row.get("requirements") else [],
            "requirements_count": len(eval(row["requirements"])) if row.get("requirements") else 0
        }
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs for matching"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            jobs.append({
                "id": row["id"],
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "location": row["location"],
                "domain": row.get("domain"),
                "requirements": eval(row["requirements"]) if row.get("requirements") else []
            })
        
        return jobs
