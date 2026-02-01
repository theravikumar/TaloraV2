# job-pipeline/scrapers/playwright_driver.py
"""
Playwright browser driver for JavaScript-rendered websites.
"""

from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from typing import Optional
from contextlib import contextmanager
from shared.config import settings


class PlaywrightDriver:
    """
    Manages Playwright browser instances.
    Supports context manager for automatic cleanup.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.headless = settings.PLAYWRIGHT_HEADLESS
        self.timeout = settings.PLAYWRIGHT_TIMEOUT
        self.user_agent = settings.USER_AGENT
    
    def start(self):
        """Start browser"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                ]
            )
    
    def stop(self):
        """Stop browser and cleanup"""
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
    
    def get_page(self) -> Page:
        """
        Create a new page with default settings.
        
        Returns:
            Playwright Page instance
        """
        if not self.browser:
            self.start()
        
        page = self.browser.new_page(
            user_agent=self.user_agent,
        )
        page.set_default_timeout(self.timeout)
        
        return page
    
    def fetch_html(self, url: str, wait_for: Optional[str] = None) -> str:
        """
        Fetch HTML from URL with optional selector wait.
        
        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for (optional)
            
        Returns:
            Page HTML content
            
        Raises:
            PlaywrightTimeout: If page load or selector wait times out
        """
        page = self.get_page()
        
        try:
            # Navigate with simpler wait strategy
            page.goto(url, wait_until='domcontentloaded')
            
            # Wait a bit for JavaScript
            page.wait_for_timeout(2000)
            
            # Wait for specific element if requested
            if wait_for:
                page.wait_for_selector(wait_for, timeout=self.timeout)
            
            # Get HTML
            html = page.content()
            
            return html
            
        finally:
            page.close()
    
    @contextmanager
    def managed_page(self):
        """
        Context manager for page that auto-closes.
        
        Usage:
            with driver.managed_page() as page:
                page.goto(url)
                # ... do stuff
        """
        page = self.get_page()
        try:
            yield page
        finally:
            page.close()
    
    def __enter__(self):
        """Support 'with' statement"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto cleanup on 'with' exit"""
        self.stop()
