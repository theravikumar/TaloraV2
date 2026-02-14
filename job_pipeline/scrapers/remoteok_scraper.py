# job_pipeline/scrapers/remoteok_scraper.py
"""
RemoteOK Free API Scraper - NO API KEY NEEDED!
Public API: https://remoteok.com/api
"""

import requests
import time
from typing import List, Dict
from datetime import datetime


class RemoteOKScraper:
    """
    Scraper for RemoteOK's free public API.
    
    Features:
    - 100% free, no API key needed
    - Returns JSON directly
    - ~1000+ remote jobs available
    - Updated daily
    """
    
    def __init__(self):
        self.base_url = "https://remoteok.com/api"
        self.headers = {
            "User-Agent": "TaloraV2 Job Matcher (Educational Project)"
        }
    
    def scrape_all_jobs(self, limit: int = None, location: str = None) -> List[Dict]:
        """
        Scrape all jobs from RemoteOK API.
        
        Args:
            limit: Max number of jobs to return (None = all)
            
        Returns:
            List of job dictionaries
        """
        try:
            print(f"Fetching jobs from RemoteOK API...")
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # RemoteOK returns array of jobs (first item is legal notice)
            all_jobs = response.json()
            
            # Skip first item (it's just metadata/legal notice)
            if all_jobs and isinstance(all_jobs, list) and len(all_jobs) > 0:
                all_jobs = all_jobs[1:]
            
            print(f"[OK] Retrieved {len(all_jobs)} jobs from RemoteOK")
            
            # Normalize to our format
            normalized_jobs = []
            for job in all_jobs:
                # Filter by location if specified
                if location:
                    job_loc = job.get('location', '').lower()
                    if location.lower() not in job_loc:
                        continue
                
                normalized = self._normalize_job(job)
                if normalized:
                    normalized_jobs.append(normalized)
                
                # Check limit
                if limit and len(normalized_jobs) >= limit:
                    break
            
            print(f"[OK] Normalized {len(normalized_jobs)} jobs matching '{location}'" if location else f"[OK] Normalized {len(normalized_jobs)} jobs")
            return normalized_jobs
            
        except Exception as e:
            print(f"[ERROR] Error scraping RemoteOK: {e}")
            return []
    
    def _normalize_job(self, raw_job: Dict) -> Dict:
        """
        Normalize RemoteOK job to our schema.
        
        RemoteOK fields:
        - id, slug, company, position, tags, logo, description
        - date, url, apply_url, location
        """
        try:
            # Generate unique job ID
            job_id = f"remoteok-{raw_job.get('id', raw_job.get('slug', 'unknown'))}"
            
            # Extract job URL
            job_url = raw_job.get('url') or raw_job.get('apply_url') or f"https://remoteok.com/remote-jobs/{raw_job.get('slug', '')}"
            
            # Build full description from available fields
            description_parts = []
            if raw_job.get('description'):
                description_parts.append(raw_job['description'])
            
            # Add tags as requirements if present
            if raw_job.get('tags'):
                tags_text = "Required skills: " + ", ".join(raw_job['tags'])
                description_parts.append(tags_text)
            
            raw_text = "\\n\\n".join(description_parts) if description_parts else "No description available"
            
            # Map to our schema
            normalized = {
                'job_id': job_id,
                'job_url': job_url,
                'source': 'remoteok',
                'company_name': raw_job.get('company', 'Unknown Company'),
                'company_url': raw_job.get('company_logo') or None,
                'job_title': raw_job.get('position', 'Unknown Position'),
                'location': raw_job.get('location', 'Remote'),
                'work_mode': 'remote',  # RemoteOK is all remote
                'employment_type': 'full-time',  # Default assumption
                'salary': raw_job.get('salary_min') or raw_job.get('salary_max') or None,
                'experience_level': None,  # Not provided by RemoteOK
                'posted_date': self._parse_date(raw_job.get('date')),
                'scraped_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'domain': self._infer_domain(raw_job.get('tags', [])),
                'is_active': True,
                'extraction_quality': 0.8,  # Good but not perfect (missing some fields)
                'raw_text': raw_text,
            }
            
            return normalized
            
        except Exception as e:
            print(f"[ERROR] Error normalizing job {raw_job.get('id')}: {e}")
            return None
    
    def _parse_date(self, date_str) -> str:
        """Parse RemoteOK datetime to ISO format"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            # RemoteOK uses Unix timestamp (epoch)
            if isinstance(date_str, (int, float)):
                dt = datetime.fromtimestamp(date_str)
                return dt.isoformat()
            return date_str
        except:
            return datetime.now().isoformat()
    
    def _infer_domain(self, tags: List[str]) -> str:
        """Infer job domain from tags"""
        if not tags:
            return None
        
        tags_lower = [t.lower() for t in tags]
        
        # Check for common domains
        if any(t in tags_lower for t in ['backend', 'api', 'python', 'node', 'django', 'fastapi']):
            return 'backend'
        if any(t in tags_lower for t in ['frontend', 'react', 'vue', 'angular', 'javascript', 'css']):
            return 'frontend'
        if any(t in tags_lower for t in ['ml', 'ai', 'machine-learning', 'data-science', 'pytorch', 'tensorflow']):
            return 'ML'
        if any(t in tags_lower for t in ['devops', 'kubernetes', 'docker', 'aws', 'cloud']):
            return 'devops'
        if any(t in tags_lower for t in ['design', 'ui', 'ux', 'figma']):
            return 'design'
        
        return 'general'


# Singleton
remoteok_scraper = RemoteOKScraper()
