"""
Firecrawl API Client
Handles all Firecrawl API interactions with proper error handling
"""

import requests
from typing import Tuple, Dict, Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from src.config import APIEndpoints, Constants, get_logger
from src.security.validators import InputValidator
from src.api.mock_data import MockDataGenerator

logger = get_logger(__name__)


class FirecrawlError(Exception):
    """Custom exception for Firecrawl API errors"""
    pass


class FirecrawlClient:
    """Firecrawl API client with retry logic and error handling"""
    
    def __init__(self, api_key: str, timeout: int = 60, test_mode: bool = False):
        """
        Initialize Firecrawl client
        
        Args:
            api_key: Firecrawl API key
            timeout: Request timeout in seconds
            test_mode: If True, use mock data instead of real API calls
        """
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = APIEndpoints.FIRECRAWL_BASE
        self.test_mode = test_mode
        
        # Configure session with retry logic
        self.session = self._create_session()
        
        if test_mode:
            logger.info("Firecrawl client initialized in TEST MODE (using mock data)")
        else:
            logger.info("Firecrawl client initialized")
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy: retry on connection errors and 5xx errors
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': f'{Constants.APP_NAME}/{Constants.APP_VERSION}'
        }
    
    def test_connection(self, test_url: str = "https://www.google.com") -> Tuple[bool, str]:
        """
        Test Firecrawl API connection
        
        Args:
            test_url: URL to test scraping (default: google.com)
            
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Testing Firecrawl connection with URL: {test_url}")
        
        # Test mode - always return success
        if self.test_mode:
            logger.info("Test mode: Simulating successful connection")
            return True, "✓ Test mode active - using mock data"
        
        try:
            response = self.session.post(
                APIEndpoints.FIRECRAWL_SCRAPE,
                headers=self._get_headers(),
                json={'url': test_url, 'formats': ['markdown']},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Firecrawl connection test successful")
                return True, "✓ Connection successful!"
            elif response.status_code == 401:
                logger.error("Firecrawl authentication failed")
                return False, "❌ Invalid API key (401 Unauthorized)"
            elif response.status_code == 402:
                logger.error("Firecrawl credits exhausted")
                return False, "❌ Payment required - check your Firecrawl credits"
            elif response.status_code == 429:
                logger.warning("Firecrawl rate limit hit")
                return False, "⚠️ Rate limit exceeded - try again later"
            else:
                logger.error(f"Firecrawl test failed: {response.status_code}")
                return False, f"❌ Error: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Firecrawl connection timeout")
            return False, "❌ Connection timeout - check your internet"
        except requests.exceptions.ConnectionError:
            logger.error("Firecrawl connection error")
            return False, "❌ Connection error - check internet or firewall"
        except Exception as e:
            logger.error(f"Firecrawl test error: {e}")
            return False, f"❌ Error: {str(e)}"
    
    def scrape_url(self, 
                   url: str, 
                   only_main_content: bool = True) -> Tuple[bool, str, Dict]:
        """
        Scrape a URL using Firecrawl API
        
        Args:
            url: URL to scrape
            only_main_content: If True, extract only main content
            
        Returns:
            Tuple of (success, content/error_message, metadata)
        """
        # Validate URL first
        is_valid, result = InputValidator.validate_url(url)
        if not is_valid:
            logger.warning(f"Invalid URL provided: {url}")
            return False, f"Invalid URL: {result}", {}
        
        url = result  # Use cleaned URL
        logger.info(f"Scraping URL: {url}")
        
        # Test mode - return mock data
        if self.test_mode:
            logger.info(f"Test mode: Returning mock data for {url}")
            content = MockDataGenerator.get_mock_scraped_content(url)
            metadata = MockDataGenerator.get_mock_metadata(url)
            return True, content, metadata
        
        try:
            payload = {
                'url': url,
                'formats': ['markdown', 'html'],
                'onlyMainContent': only_main_content
            }
            
            response = self.session.post(
                APIEndpoints.FIRECRAWL_SCRAPE,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    markdown_content = data.get('data', {}).get('markdown', '')
                    metadata = data.get('data', {}).get('metadata', {})
                    
                    logger.info(f"Successfully scraped {len(markdown_content)} characters from {url}")
                    return True, markdown_content, metadata
                else:
                    error_msg = data.get('error', 'Unknown error')
                    logger.error(f"Firecrawl returned error: {error_msg}")
                    return False, f"Scraping failed: {error_msg}", {}
            
            elif response.status_code == 401:
                logger.error("Firecrawl authentication failed during scraping")
                return False, "Invalid Firecrawl API key", {}
            
            elif response.status_code == 402:
                logger.error("Firecrawl credits exhausted")
                return False, "Firecrawl credits exhausted - please top up", {}
            
            elif response.status_code == 429:
                logger.warning("Firecrawl rate limit exceeded")
                return False, "Rate limit exceeded - please wait and try again", {}
            
            else:
                error_text = response.text[:200]
                logger.error(f"Firecrawl HTTP error {response.status_code}: {error_text}")
                return False, f"HTTP {response.status_code}: {error_text}", {}
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout scraping {url}")
            return False, f"Scraping timeout ({self.timeout}s exceeded)", {}
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error scraping {url}: {e}")
            return False, "Connection error - check internet connection", {}
        
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
            return False, f"Scraping error: {str(e)}", {}
    
    def scrape_multiple(self, urls: list[str]) -> list[Dict]:
        """
        Scrape multiple URLs (convenience method)
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of results dictionaries
        """
        results = []
        
        for idx, url in enumerate(urls, 1):
            logger.info(f"Scraping {idx}/{len(urls)}: {url}")
            
            success, content, metadata = self.scrape_url(url)
            
            results.append({
                'url': url,
                'success': success,
                'content': content,
                'metadata': metadata
            })
        
        return results
    
    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("Firecrawl client session closed")
