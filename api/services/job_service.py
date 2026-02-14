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
        employment_type: Optional[str] = None,
        ids: Optional[str] = None,  # Comma-separated job IDs for smart search
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
        query = """
            SELECT j.*, (SELECT COUNT(*) FROM job_work_units wu WHERE wu.job_id = j.job_id) as req_count 
            FROM jobs j 
            WHERE j.is_active = 1
        """
        params = []
        
        # If IDs are specified (smart search mode), filter by those
        if ids:
            id_list = ids.split(",")
            placeholders = ",".join(["?" for _ in id_list])
            query += f" AND j.job_id IN ({placeholders})"
            params.extend(id_list)
        else:
            # Regular search filters
            if keywords:
                keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
                keyword_clauses = []
                for k in keyword_list:
                    keyword_clauses.append("(j.job_role LIKE ? COLLATE NOCASE OR j.domain LIKE ? COLLATE NOCASE OR j.job_title LIKE ? COLLATE NOCASE OR j.company_name LIKE ? COLLATE NOCASE)")
                    params.extend([f"%{k}%", f"%{k}%", f"%{k}%", f"%{k}%"])
                if keyword_clauses:
                    query += f" AND ({' OR '.join(keyword_clauses)})"
            
            if location:
                location_list = [l.strip() for l in location.split(",") if l.strip()]
                location_clauses = []
                for l in location_list:
                    location_clauses.append("j.location LIKE ? COLLATE NOCASE")
                    params.append(f"%{l}%")
                if location_clauses:
                    query += f" AND ({' OR '.join(location_clauses)})"
            
            if employment_type:
                query += " AND j.employment_type = ? COLLATE NOCASE"
                params.append(employment_type)
        
        # Get total count (using a subquery to avoid complex replacement)
        count_params = params[:]
        cursor.execute(f"SELECT COUNT(*) FROM ({query})", count_params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        query += f" ORDER BY j.posted_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            req_count = row["req_count"]
            
            jobs.append({
                "job_id": row["job_id"],
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "location": row["location"],
                "domain": row["domain"],
                "posted_date": row["posted_date"],
                "salary": row["salary"] if "salary" in row.keys() else None,
                "work_mode": row["work_mode"] if "work_mode" in row.keys() else None,
                "requirements_count": req_count,
                "job_url": row["job_url"] if "job_url" in row.keys() else None,
                "job_description": row["job_description"] if "job_description" in row.keys() else None
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
        if not row:
            conn.close()
            return None
            
        # Get work units
        try:
            cursor.execute("SELECT * FROM job_work_units WHERE job_id = ?", (job_id,))
            wu_rows = cursor.fetchall()
            work_units = []
            for wu in wu_rows:
                work_units.append({
                    "priority": wu["priority"],
                    "action": wu["action"],
                    "object": wu["object"],
                    "tools": json.loads(wu["tools"]) if wu["tools"] else [],
                    "constraints": json.loads(wu["constraints"]) if wu["constraints"] else [],
                    "outcome": wu["outcome"]
                })
        except Exception as e:
            print(f"Error fetching work units: {e}")
            work_units = []
        
        conn.close()
        
        return {
            "job_id": row["job_id"],
            "job_title": row["job_title"],
            "company_name": row["company_name"],
            "location": row["location"],
            "domain": row["domain"],
            "posted_date": row["posted_date"],
            "salary": row["salary_raw"] if "salary_raw" in row.keys() else None,
            "work_mode": row["work_mode"] if "work_mode" in row.keys() else None,
            "employment_type": row["employment_type"] if "employment_type" in row.keys() else None,
            "experience_level": row["experience_raw"] if "experience_raw" in row.keys() else None,
            "raw_text": row["raw_text"] if "raw_text" in row.keys() else None,
            # Use job_description if available, fallback to raw_text, then description
            "description": (row["job_description"] if "job_description" in row.keys() and row["job_description"] else 
                           (row["raw_text"] if "raw_text" in row.keys() and row["raw_text"] else 
                           (row["description"] if "description" in row.keys() else None))),
            "job_description": row["job_description"] if "job_description" in row.keys() else None,
            "job_url": row["job_url"] if "job_url" in row.keys() else None,
            "work_units": work_units,
            "requirements_count": len(work_units)
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
            jobs.append({
                "id": row["job_id"],
                "job_id": row["job_id"],
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "location": row["location"],
                "domain": row["domain"]
            })
        
        return jobs
    
    def get_unique_job_titles(self, query: Optional[str] = None) -> List[str]:
        """Get unique suggestions for 'Job Role / Skill' from roles, domains, and titles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Combine roles, domains, and titles
        parts = []
        
        # 1. Job Roles
        sql_roles = "SELECT DISTINCT job_role FROM jobs WHERE is_active = 1 AND job_role IS NOT NULL"
        if query:
            sql_roles += " AND job_role LIKE ?"
            cursor.execute(sql_roles, (f"%{query}%",))
        else:
            cursor.execute(sql_roles)
        parts.extend([row[0] for row in cursor.fetchall()])
        
        # 2. Domains
        sql_domains = "SELECT DISTINCT domain FROM jobs WHERE is_active = 1 AND domain IS NOT NULL"
        if query:
            sql_domains += " AND domain LIKE ?"
            cursor.execute(sql_domains, (f"%{query}%",))
        else:
            cursor.execute(sql_domains)
        parts.extend([row[0] for row in cursor.fetchall()])
        
        conn.close()
        
        # Deduplicate and limit
        unique_suggestions = sorted(list(set(parts)))[:50]
        
        return unique_suggestions
    
    def get_unique_locations(self, query: Optional[str] = None) -> List[str]:
        """Get unique locations for autocomplete"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT DISTINCT location FROM jobs WHERE is_active = 1"
        params = []
        
        if query:
            sql += " AND location LIKE ?"
            params.append(f"%{query}%")
        
        sql += " ORDER BY location LIMIT 50"
        
        cursor.execute(sql, params)
        locations = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return locations
