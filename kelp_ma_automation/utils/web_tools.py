"""
Web Scraping Tools
Playwright-based scraper with fallback to requests+BeautifulSoup.
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


# Domain-specific pages to scrape
DOMAIN_PAGES = {
    'manufacturing': ['about', 'about-us', 'company', 'products', 'services', 
                      'manufacturing', 'facilities', 'quality', 'certifications', 'capabilities'],
    'technology': ['about', 'about-us', 'company', 'solutions', 'services',
                   'technologies', 'case-studies', 'clients', 'partners'],
    'logistics': ['about', 'about-us', 'company', 'services', 'solutions',
                  'network', 'tracking', 'sustainability', 'warehousing'],
    'consumer': ['about', 'about-us', 'company', 'products', 'our-story',
                 'testimonials', 'shop', 'collections'],
    'healthcare': ['about', 'about-us', 'company', 'products', 'therapeutic-areas',
                   'research', 'r-and-d', 'approvals', 'manufacturing'],
    'infrastructure': ['about', 'about-us', 'company', 'projects', 'portfolio',
                       'expertise', 'services', 'clients'],
    'chemicals': ['about', 'about-us', 'company', 'products', 'applications',
                  'quality', 'manufacturing', 'certifications'],
    'automotive': ['about', 'about-us', 'company', 'products', 'customers',
                   'technology', 'capabilities', 'quality'],
}


def simple_scrape(url: str, timeout: int = 15) -> Optional[str]:
    """
    Simple HTTP-based scraping (no JavaScript).
    
    Args:
        url: URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text content or None
    """
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Try trafilatura first (better content extraction)
        if TRAFILATURA_AVAILABLE:
            text = trafilatura.extract(response.text, 
                                       include_links=False,
                                       include_images=False)
            if text:
                return text
        
        # Fallback to BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 
                         'aside', 'noscript', 'iframe']):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text[:10000]  # Limit size
        
    except requests.RequestException as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return None


class WebScraper:
    """
    Web scraper with Playwright support for JS-heavy sites.
    Falls back to simple requests if Playwright unavailable.
    """
    
    def __init__(self, use_playwright: bool = True):
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.last_request_time = 0
        self.min_delay = 1.0  # Minimum seconds between requests
        
        if use_playwright and not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available. Using requests fallback.")
            logger.info("Install with: pip install playwright && playwright install chromium")
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()
    
    def scrape(self, base_url: str, domain: str = 'manufacturing') -> Dict[str, str]:
        """
        Scrape company website for relevant content.
        
        Args:
            base_url: Company website URL
            domain: Company domain for page selection
            
        Returns:
            Dict mapping page names to extracted content
        """
        if not base_url:
            logger.warning("No URL provided for scraping")
            return {}
        
        # Normalize URL
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
        
        if self.use_playwright:
            return asyncio.run(self._scrape_with_playwright(base_url, domain))
        else:
            return self._scrape_with_requests(base_url, domain)
    
    def _scrape_with_requests(self, base_url: str, domain: str) -> Dict[str, str]:
        """Scrape using requests library."""
        scraped = {}
        
        # Scrape homepage
        self._rate_limit()
        homepage_content = simple_scrape(base_url)
        if homepage_content:
            scraped['homepage'] = homepage_content
        
        # Get domain-specific pages
        pages = DOMAIN_PAGES.get(domain, DOMAIN_PAGES['manufacturing'])
        
        for page_path in pages:
            self._rate_limit()
            page_url = urljoin(base_url + '/', page_path)
            
            content = simple_scrape(page_url)
            if content and len(content) > 100:
                scraped[page_path] = content
                logger.info(f"Scraped: {page_url} ({len(content)} chars)")
            
            # Limit pages scraped
            if len(scraped) >= 6:
                break
        
        return scraped
    
    async def _scrape_with_playwright(self, base_url: str, domain: str) -> Dict[str, str]:
        """Scrape using Playwright for JS rendering."""
        scraped = {}
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = await browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US'
                )
                
                page = await context.new_page()
                
                # Set extra headers
                await page.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml',
                })
                
                try:
                    # Scrape homepage
                    await page.goto(base_url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    content = await page.content()
                    text = self._extract_text(content)
                    if text:
                        scraped['homepage'] = text
                    
                    # Scrape additional pages
                    pages = DOMAIN_PAGES.get(domain, DOMAIN_PAGES['manufacturing'])
                    
                    for page_path in pages[:5]:  # Limit pages
                        try:
                            page_url = urljoin(base_url + '/', page_path)
                            await page.goto(page_url, wait_until='networkidle', timeout=15000)
                            await page.wait_for_timeout(1500)
                            
                            content = await page.content()
                            text = self._extract_text(content)
                            if text and len(text) > 100:
                                scraped[page_path] = text
                                logger.info(f"Scraped: {page_url}")
                        except Exception as e:
                            logger.debug(f"Page {page_path} not found: {e}")
                            continue
                        
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"Playwright scraping failed: {e}")
            # Fallback to requests
            return self._scrape_with_requests(base_url, domain)
        
        return scraped
    
    def _extract_text(self, html: str) -> str:
        """Extract clean text from HTML."""
        if TRAFILATURA_AVAILABLE:
            text = trafilatura.extract(html,
                                       include_links=False,
                                       include_images=False,
                                       no_fallback=False)
            if text:
                return text[:10000]
        
        # Fallback to BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        text = ' '.join(text.split())
        
        return text[:10000]
    
    def get_page_title(self, url: str) -> Optional[str]:
        """Get page title for citation."""
        try:
            response = requests.get(url, headers={'User-Agent': USER_AGENTS[0]}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            return title.get_text().strip() if title else None
        except:
            return None


# Test
if __name__ == "__main__":
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.centumelectronics.com"
    domain = sys.argv[2] if len(sys.argv) > 2 else "manufacturing"
    
    print(f"Scraping: {url}")
    print(f"Domain: {domain}")
    print("-" * 50)
    
    scraper = WebScraper(use_playwright=False)  # Use requests for testing
    results = scraper.scrape(url, domain)
    
    print(f"\nScraped {len(results)} pages:")
    for page_name, content in results.items():
        print(f"  {page_name}: {len(content)} chars")
        if len(content) > 200:
            print(f"    Preview: {content[:200]}...")
