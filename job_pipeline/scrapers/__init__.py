# job_pipeline/scrapers/__init__.py

from .base_scraper import BaseScraper
from .playwright_driver import PlaywrightDriver
from .ambitionbox import AmbitionBoxScraper
from .remoteok_scraper import remoteok_scraper, RemoteOKScraper
from .arbeitnow_scraper import arbeitnow_scraper, ArbeitNowScraper
from .linkedin_scraper import linkedin_scraper, LinkedInScraper
from .multi_source_scraper import multi_source_scraper, MultiSourceScraper

__all__ = [
    "BaseScraper",
    "PlaywrightDriver",
    "AmbitionBoxScraper",
    "remoteok_scraper",
    "RemoteOKScraper",
    "arbeitnow_scraper",
    "ArbeitNowScraper",
    "multi_source_scraper",
    "MultiSourceScraper",
]
