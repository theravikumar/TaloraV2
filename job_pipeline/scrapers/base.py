# job-pipeline/scrapers/base.py
"""
Base scraper interface for all website scrapers.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from shared.config import settings


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Enforces consistent interface and provides common utilities.
    """
    
    def __init__(self):
        self.delay = settings.SCRAPING_DELAY
        self.max_retries = settings.MAX_RETRIES
    
    @abstractmethod
    def scrape_companies(self, max_companies: int) -> List[str]:
        """
        Scrape list of company identifiers.
        
        Args:
            max_companies: Maximum number of companies to scrape
            
        Returns:
            List of company identifiers (slugs, IDs, etc.)
        """
        pass
    
    @abstractmethod
    def scrape_jobs(self, company_id: str) -> List[Dict]:
        """
        Scrape jobs for a specific company.
        
        Args:
            company_id: Company identifier
            
        Returns:
            List of raw job dictionaries with at minimum:
            - job_url: str
            - job_title: str
            - company_name: str
        """
        pass
    
    def rate_limit(self):
        """Sleep to avoid getting blocked"""
        time.sleep(self.delay)
    
    def retry_on_failure(self, func, *args, **kwargs):
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Function result
            
        Raises:
            Exception if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
        
        raise Exception("Max retries exceeded")
