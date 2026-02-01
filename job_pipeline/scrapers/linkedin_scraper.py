# job_pipeline/scrapers/linkedin_scraper.py
"""
LinkedIn Jobs Guest API Scraper - NO API KEY NEEDED!
Public API: https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search

Legal: This uses LinkedIn's public guest API which does not require authentication.
It's the same API used when you visit linkedin.com/jobs without being logged in.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import time


class LinkedInScraper:
    """
    Scraper for LinkedIn's public guest job search API.
    
    Features:
    - 100% free, no API key
    - Works for India, US, Europe
    - Returns structured HTML that we parse
    - Rate limit: ~1000 requests/day (very generous)
    """
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def scrape_jobs(
        self, 
        keywords: str = "software engineer",
        location: str = "India",
        limit: int = 100
    ) -> List[Dict]:
        """
        Scrape jobs from LinkedIn guest API.
        
        Args:
            keywords: Job search keywords
            location: Location (India, United States, Europe, etc.)
            limit: Max jobs to return
            
        Returns:
            List of normalized job dictionaries
        """
        jobs = []
        
        print(f"Scraping LinkedIn jobs: '{keywords}' in '{location}'")
        
        # LinkedIn returns 25 jobs per page
        for start in range(0, limit, 25):
            try:
                page_jobs = self._scrape_page(keywords, location, start)
                jobs.extend(page_jobs)
                
                if len(page_jobs) < 25:
                    # No more jobs available
                    break
                
                # Be polite - small delay between pages
                time.sleep(1)
                
            except Exception as e:
                print(f"[ERROR] Error scraping page {start}: {e}")
                break
        
        print(f"[OK] Retrieved {len(jobs)} jobs from LinkedIn")
        return jobs[:limit]
    
    def scrape_multi_location(
        self,
        keywords: str = "software engineer",
        locations: List[str] = None,
        jobs_per_location: int = 100
    ) -> List[Dict]:
        """
        Scrape jobs from multiple locations.
        
        Args:
            keywords: Job search keywords
            locations: List of locations (default: India, US, Europe)
            jobs_per_location: Jobs to get per location
            
        Returns:
            Combined list of jobs from all locations
        """
        if locations is None:
            locations = ["India", "United States", "Europe"]
        
        all_jobs = []
        
        for location in locations:
            print(f"\nSearching in: {location}")
            jobs = self.scrape_jobs(keywords, location, jobs_per_location)
            all_jobs.extend(jobs)
            time.sleep(2)  # Polite delay between location changes
        
        return all_jobs
    
    def _scrape_page(self, keywords: str, location: str, start: int) -> List[Dict]:
        """Scrape a single page of results"""
        params = {
            "keywords": keywords,
            "location": location,
            "start": start,
            "sortBy": "DD"  # Date descending (newest first)
        }
        
        response = requests.get(
            self.base_url,
            params=params,
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all job cards
        job_cards = soup.find_all('li')
        
        jobs = []
        for card in job_cards:
            try:
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                # Skip malformed cards
                continue
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse a single job card into our schema"""
        try:
            # Extract job link and ID
            link_elem = card.find('a', class_='base-card__full-link')
            if not link_elem:
                return None
            
            job_url = link_elem.get('href', '')
            
            # Extract job ID from URL
            job_id_match = job_url.split('/')[-1].split('?')[0] if job_url else None
            job_id = f"linkedin-{job_id_match}" if job_id_match else f"linkedin-{hash(job_url)}"
            
            # Extract title
            title_elem = card.find('h3', class_='base-search-card__title')
            title = title_elem.text.strip() if title_elem else "Unknown"
            
            # Extract company
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.text.strip() if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.text.strip() if location_elem else "Remote"
            
            # Extract posted date
            time_elem = card.find('time')
            posted_date = time_elem.get('datetime') if time_elem else datetime.now().isoformat()
            
            # Build normalized job
            normalized = {
                'job_id': job_id,
                'job_url': job_url,
                'source': 'linkedin',
                'company_name': company,
                'company_url': None,
                'job_title': title,
                'location': location,
                'work_mode': self._infer_work_mode(location, title),
                'employment_type': 'full-time',  # LinkedIn doesn't provide this in guest API
                'salary': None,  # Not in guest API
                'experience_level': None,  # Not in guest API
                'posted_date': posted_date,
                'scraped_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'domain': self._infer_domain(title),
                'is_active': True,
                'extraction_quality': 0.7,  # Good but missing some fields
                'raw_text': f"{title} at {company} - {location}",  # Will fetch full description later
            }
            
            return normalized
            
        except Exception as e:
            return None
    
    def _infer_work_mode(self, location: str, title: str) -> str:
        """Infer work mode from location and title"""
        location_lower = location.lower()
        title_lower = title.lower()
        
        if 'remote' in location_lower or 'remote' in title_lower:
            return 'remote'
        elif 'hybrid' in location_lower or 'hybrid' in title_lower:
            return 'hybrid'
        else:
            return 'onsite'
    
    def _infer_domain(self, title: str) -> str:
        """Infer job domain from title"""
        title_lower = title.lower()
        
        if any(term in title_lower for term in ['backend', 'api', 'server', 'python', 'java', 'node']):
            return 'backend'
        if any(term in title_lower for term in ['frontend', 'react', 'vue', 'angular', 'ui']):
            return 'frontend'
        if any(term in title_lower for term in ['ml', 'machine learning', 'ai', 'data scientist', 'deep learning']):
            return 'ML'
        if any(term in title_lower for term in ['devops', 'sre', 'cloud', 'kubernetes', 'infrastructure']):
            return 'devops'
        if any(term in title_lower for term in ['full stack', 'fullstack']):
            return 'fullstack'
        if any(term in title_lower for term in ['mobile', 'android', 'ios', 'flutter']):
            return 'mobile'
        
        return 'general'


# Singleton
linkedin_scraper = LinkedInScraper()
