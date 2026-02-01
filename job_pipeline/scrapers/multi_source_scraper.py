# job_pipeline/scrapers/multi_source_scraper.py
"""
Multi-Source Free Job Scraper
Combines multiple free APIs to get maximum job coverage at $0 cost.
Supports: India, US, Europe
"""

from typing import List, Dict
from .remoteok_scraper import remoteok_scraper
from .arbeitnow_scraper import arbeitnow_scraper
from .linkedin_scraper import linkedin_scraper


class MultiSourceScraper:
    """
    Aggregates jobs from multiple free sources.
    
    Sources:
    1. LinkedIn Guest API (~300+ jobs per location)
    2. RemoteOK (~1000+ remote jobs)
    3. ArbeitNow (~500+ European/remote jobs)
    4. [Future] Company career pages
    
    Regions supported: India, US, Europe
    Total potential: 2000+ jobs/day with $0 cost
    """
    
    def __init__(self):
        self.sources = {
            'linkedin': linkedin_scraper,
            'remoteok': remoteok_scraper,
            'arbeitnow': arbeitnow_scraper,
        }
    
    def scrape_all_sources(
        self, 
        limit_per_source: int = None,
        regions: List[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Scrape from all available free sources.
        
        Args:
            limit_per_source: Max jobs per source (None = all available)
            regions: Regions to scrape (default: ["India", "United States", "Europe"])
            
        Returns:
            Dictionary mapping source name to jobs list
        """
        if regions is None:
            regions = ["India", "United States", "Europe"]
        
        results = {}
        
        print("=" * 60)
        print("MULTI-SOURCE FREE JOB SCRAPING")
        print(f"Regions: {', '.join(regions)}")
        print("=" * 60)
        
        # Scrape LinkedIn (supports region filtering)
        print("\n1. LinkedIn Guest API (India, US, Europe)")
        try:
            linkedin_jobs = linkedin_scraper.scrape_multi_location(
                keywords="software engineer",
                locations=regions,
                jobs_per_location=limit_per_source or 100
            )
            results['linkedin'] = linkedin_jobs
            print(f"[OK] LinkedIn: {len(linkedin_jobs)} jobs")
        except Exception as e:
            print(f"[ERROR] LinkedIn failed: {e}")
            results['linkedin'] = []
        
        # Scrape RemoteOK
        print("\n2. RemoteOK (Free Public API - Remote Jobs)")
        try:
            remoteok_jobs = remoteok_scraper.scrape_all_jobs(limit=limit_per_source)
            results['remoteok'] = remoteok_jobs
            print(f"[OK] RemoteOK: {len(remoteok_jobs)} jobs")
        except Exception as e:
            print(f"[ERROR] RemoteOK failed: {e}")
            results['remoteok'] = []
        
        # Scrape ArbeitNow
        print("\n3. ArbeitNow (Free API - European/Remote)")
        try:
            arbeitnow_jobs = arbeitnow_scraper.scrape_jobs(limit=limit_per_source or 100)
            results['arbeitnow'] = arbeitnow_jobs
            print(f"[OK] ArbeitNow: {len(arbeitnow_jobs)} jobs")
        except Exception as e:
            print(f"[ERROR] ArbeitNow failed: {e}")
            results['arbeitnow'] = []
        
        # Summary
        total_jobs = sum(len(jobs) for jobs in results.values())
        print("\n" + "=" * 60)
        print(f"TOTAL: {total_jobs} jobs from {len(results)} sources")
        print("=" * 60)
        
        return results
    
    def scrape_and_merge(self, limit_per_source: int = None, deduplicate: bool = True) -> List[Dict]:
        """
        Scrape all sources and return merged list.
        
        Args:
            limit_per_source: Max jobs per source
            deduplicate: Remove duplicate jobs (by company + title)
            
        Returns:
            Merged list of all jobs
        """
        results = self.scrape_all_sources(limit_per_source)
        
        # Merge all jobs
        all_jobs = []
        for source, jobs in results.items():
            all_jobs.extend(jobs)
        
        # Deduplicate if requested
        if deduplicate:
            all_jobs = self._deduplicate_jobs(all_jobs)
            print(f"\\n[OK] After deduplication: {len(all_jobs)} unique jobs")
        
        return all_jobs
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate jobs based on company + title.
        Keeps the first occurrence.
        """
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create key from company + title (normalized)
            key = (
                job['company_name'].lower().strip(),
                job['job_title'].lower().strip()
            )
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def get_daily_jobs(self) -> List[Dict]:
        """
        Recommended daily scraping routine.
        Gets all jobs from all free sources, deduplicated.
        
        Returns:
            List of unique jobs (typically 800-1200 jobs/day)
        """
        print("\\nDAILY JOB COLLECTION")
        print("Strategy: Scrape all free sources, deduplicate, store")
        print("=" * 60)
        
        jobs = self.scrape_and_merge(deduplicate=True)
        
        print(f"\\n[OK] Daily collection complete: {len(jobs)} unique jobs")
        return jobs


# Singleton
multi_source_scraper = MultiSourceScraper()
