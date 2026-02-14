# job_pipeline/scrapers/arbeitnow_scraper.py
"""
ArbeitNow Free API Scraper - NO API KEY NEEDED!
Focuses on European and remote jobs.
"""

import requests
from typing import List, Dict
from datetime import datetime


class ArbeitNowScraper:
    """
    Scraper for ArbeitNow's free API.
    
    Features:
    - 100% free, no API key
    - European + remote jobs
    - Aggregates from multiple ATS (Greenhouse, SmartRecruiters, etc.)
    """
    
    def __init__(self):
        self.base_url = "https://www.arbeitnow.com/api/job-board-api"
        self.headers = {
            "User-Agent": "TaloraV2 Job Matcher (Educational Project)"
        }
    
    def scrape_jobs(self, limit: int = 100) -> List[Dict]:
        """
        Scrape jobs from ArbeitNow API.
        
        Args:
            limit: Max jobs to retrieve (API returns 50 per page)
        """
        try:
            jobs = []
            page = 1
            
            while len(jobs) < limit:
                print(f"Fetching page {page} from ArbeitNow...")
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params={'page': page},
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                page_jobs = data.get('data', [])
                
                if not page_jobs:
                    break
                
                for job in page_jobs:
                    normalized = self._normalize_job(job)
                    if normalized:
                        jobs.append(normalized)
                
                if len(jobs) >= limit or len(page_jobs) < 50:
                    break
                
                page += 1
            
            print(f"[OK] Retrieved {len(jobs)} jobs from ArbeitNow")
            return jobs[:limit]
            
        except Exception as e:
            print(f"[ERROR] Error scraping ArbeitNow: {e}")
            return []
    
    def _normalize_job(self, raw_job: Dict) -> Dict:
        """Normalize ArbeitNow job to our schema"""
        try:
            job_id = f"arbeitnow-{raw_job.get('slug', 'unknown')}"
            
            normalized = {
                'job_id': job_id,
                'job_url': raw_job.get('url', ''),
                'source': 'arbeitnow',
                'company_name': raw_job.get('company_name', 'Unknown'),
                'company_url': None,
                'job_title': raw_job.get('title', 'Unknown'),
                'location': raw_job.get('location', 'Remote') if isinstance(raw_job.get('location'), str) else ', '.join(raw_job.get('location', ['Remote'])),
                'work_mode': 'remote' if raw_job.get('remote') else 'onsite',
                'employment_type': raw_job.get('job_types', ['full-time'])[0] if raw_job.get('job_types') else 'full-time',
                'salary': None,
                'experience_level': None,
                'posted_date': raw_job.get('created_at', datetime.now().isoformat()),
                'scraped_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'domain': self._infer_domain(raw_job.get('tags', [])),
                'is_active': True,
                'extraction_quality': 0.8,
                'raw_text': raw_job.get('description', 'No description'),
            }
            
            return normalized
        except Exception as e:
            print(f"[ERROR] Error normalizing ArbeitNow job: {e}")
            return None
    
    def _infer_domain(self, tags: List[str]) -> str:
        """Infer domain from tags"""
        if not tags:
            return 'general'
        
        tags_lower = [t.lower() for t in tags]
        
        if any(t in tags_lower for t in ['backend', 'python', 'node', 'api']):
            return 'backend'
        if any(t in tags_lower for t in ['frontend', 'react', 'javascript']):
            return 'frontend'
        if any(t in tags_lower for t in ['ml', 'ai', 'data']):
            return 'ML'
        if any(t in tags_lower for t in ['devops', 'kubernetes']):
            return 'devops'
        
        return 'general'


# Singleton
arbeitnow_scraper = ArbeitNowScraper()
