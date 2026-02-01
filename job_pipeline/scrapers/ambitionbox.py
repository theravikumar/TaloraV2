# job-pipeline/scrapers/ambitionbox.py
"""
AmbitionBox scraper for company and job listings.
"""

from bs4 import BeautifulSoup
from typing import List, Dict
from .base import BaseScraper
from .playwright_driver import PlaywrightDriver


class AmbitionBoxScraper(BaseScraper):
    """
    Scrapes companies and jobs from AmbitionBox.
    
    URL patterns:
    - Companies list: https://www.ambitionbox.com/list-of-companies?page=N
    - Company jobs: https://www.ambitionbox.com/jobs/{company-slug}-jobs-cmp
    """
    
    BASE_URL = "https://www.ambitionbox.com"
    
    def __init__(self):
        super().__init__()
        self.driver = PlaywrightDriver()
    
    def scrape_companies(self, max_companies: int = 10) -> List[str]:
        """
        Scrape company slugs from list pages.
        
        Args:
            max_companies: Maximum companies to scrape
            
        Returns:
            List of company slugs (e.g., "google", "amazon")
        """
        companies = []
        page_num = 1
        
        self.driver.start()
        
        try:
            while len(companies) < max_companies:
                url = f"{self.BASE_URL}/list-of-companies?page={page_num}"
                print(f"Scraping companies page {page_num}...")
                
                html = self.driver.fetch_html(
                    url,
                    wait_for=".companyCardWrapper"  # Wait for company cards
                )
                
                soup = BeautifulSoup(html, 'lxml')
                
                # Find company cards
                cards = soup.select(".companyCardWrapper")
                
                if not cards:
                    print(f"No companies found on page {page_num}, stopping")
                    break
                
                for card in cards:
                    if len(companies) >= max_companies:
                        break
                    
                    # Extract company slug from job link
                    job_link = card.select_one('a[href*="-jobs-cmp"]')
                    if job_link:
                        href = job_link.get('href', '')
                        # Extract slug from "/jobs/google-jobs-cmp"
                        if '/jobs/' in href and '-jobs-cmp' in href:
                            slug = href.split('/jobs/')[1].split('-jobs-cmp')[0]
                            if slug and slug not in companies:
                                companies.append(slug)
                                print(f"  Found: {slug}")
                
                page_num += 1
                self.rate_limit()
                
        finally:
            self.driver.stop()
        
        print(f"[OK] Scraped {len(companies)} companies")
        return companies
    
    def scrape_jobs(self, company_slug: str) -> List[Dict]:
        """
        Scrape job listings for a company.
        
        Args:
            company_slug: Company slug (e.g., "google")
            
        Returns:
            List of job dictionaries with:
            - job_url: Full URL to job posting
            - job_title: Job title
            - company_name: Company name
            - location: Job location (if available)
            - raw_html: Full HTML for later normalization
        """
        url = f"{self.BASE_URL}/jobs/{company_slug}-jobs-cmp"
        print(f"Scraping jobs from: {url}")
        
        self.driver.start()
        
        try:
            html = self.driver.fetch_html(
                url,
                wait_for=".job-card, .no-jobs"  # Wait for jobs or no-jobs message
            )
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Check for no jobs
            if soup.select_one('.no-jobs'):
                print(f"No jobs found for {company_slug}")
                return []
            
            # Find job cards
            job_cards = soup.select('.job-card')
            
            if not job_cards:
                print(f"Warning: No job cards found for {company_slug}")
                return []
            
            jobs = []
            
            for card in job_cards:
                try:
                    # Extract job URL
                    title_link = card.select_one('a.job-title-link, h2 a, a[href*="/overview"]')
                    if not title_link:
                        continue
                    
                    job_url = title_link.get('href', '')
                    if not job_url.startswith('http'):
                        job_url = self.BASE_URL + job_url
                    
                    # Extract title
                    job_title = title_link.get_text(strip=True)
                    
                    # Extract company name (might be in different places)
                    company_elem = card.select_one('.company-name, .company')
                    company_name = company_elem.get_text(strip=True) if company_elem else company_slug.replace('-', ' ').title()
                    
                    # Extract location
                    location_elem = card.select_one('.location, .job-location')
                    location = location_elem.get_text(strip=True) if location_elem else None
                    
                    # Store job
                    jobs.append({
                        'job_url': job_url,
                        'job_title': job_title,
                        'company_name': company_name,
                        'location': location,
                        'source': 'ambitionbox',
                        'raw_html': str(card),  # Store card HTML for later processing
                    })
                    
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
            
            print(f"[OK] Found {len(jobs)} jobs for {company_slug}")
            return jobs
            
        finally:
            self.driver.stop()
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'driver'):
            self.driver.stop()
