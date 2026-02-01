# job_pipeline/scrapers/base_scraper.py
"""
Base scraper interface - all scrapers inherit from this.
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    """
    
    @abstractmethod
    def scrape_jobs(self, **kwargs) -> List[Dict]:
        """
        Scrape jobs from the source.
        
        Returns:
            List of job dictionaries in our normalized format
        """
        pass
