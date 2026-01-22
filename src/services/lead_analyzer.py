"""
Lead Analyzer Service
Orchestrates the complete lead analysis workflow with RAG integration
"""

from typing import Dict, Tuple, Optional
import time

from src.config import AppConfig, Constants, get_logger
from src.api import FirecrawlClient, OpenAIClient, AnthropicClient
from src.models.lead import Lead
from src.services.data_manager import DataManager

logger = get_logger(__name__)


class LeadAnalyzerError(Exception):
    """Custom exception for lead analysis errors"""
    pass


class LeadAnalyzer:
    """Orchestrates lead scraping and AI analysis with RAG support"""
    
    def __init__(self, config: AppConfig, data_manager: DataManager, 
                 knowledge_base=None):
        """
        Initialize LeadAnalyzer
        
        Args:
            config: Application configuration
            data_manager: DataManager instance
            knowledge_base: Optional KnowledgeBaseService instance for RAG
        """
        self.config = config
        self.data_manager = data_manager
        self.knowledge_base = knowledge_base
        
        # Initialize API clients
        self.firecrawl_client = None
        self.ai_client = None
        
        self._initialize_clients()
        
        if self.knowledge_base:
            logger.info("LeadAnalyzer initialized with Knowledge Base support")
        else:
            logger.info("LeadAnalyzer initialized (no Knowledge Base)")
    
    def _initialize_clients(self):
        """Initialize API clients based on configuration"""
        # Firecrawl client - use test mode if no API key
        if self.config.has_valid_firecrawl_key():
            self.firecrawl_client = FirecrawlClient(
                api_key=self.config.firecrawl_api_key,
                timeout=self.config.firecrawl_timeout,
                test_mode=False
            )
            logger.info("Firecrawl client initialized")
        else:
            # Initialize in test mode without API key
            self.firecrawl_client = FirecrawlClient(
                api_key="test-mode",
                timeout=self.config.firecrawl_timeout,
                test_mode=True
            )
            logger.warning("Firecrawl API key not configured - using TEST MODE with mock data")
        
        # AI client - use test mode if no API key
        if self.config.ai_provider == "OpenAI" and self.config.openai_api_key:
            self.ai_client = OpenAIClient(
                api_key=self.config.openai_api_key,
                timeout=self.config.ai_timeout,
                test_mode=False
            )
            logger.info("OpenAI client initialized")
        elif self.config.ai_provider == "Anthropic" and self.config.anthropic_api_key:
            self.ai_client = AnthropicClient(
                api_key=self.config.anthropic_api_key,
                timeout=self.config.ai_timeout,
                test_mode=False
            )
            logger.info("Anthropic client initialized")
        else:
            # Use OpenAI in test mode as default when no AI key configured
            self.ai_client = OpenAIClient(
                api_key="test-mode",
                timeout=self.config.ai_timeout,
                test_mode=True
            )
            logger.warning("AI API key not configured - using TEST MODE with mock analysis")
    
    def test_firecrawl_connection(self) -> Tuple[bool, str]:
        """Test Firecrawl API connection"""
        if not self.firecrawl_client:
            return False, "Firecrawl client not initialized"
        
        return self.firecrawl_client.test_connection()
    
    def analyze_single_url(self, url: str) -> Tuple[bool, str, Lead]:
        """
        Analyze a single URL and create Lead
        
        Args:
            url: URL to analyze
            
        Returns:
            Tuple of (success, message, Lead or None)
        """
        logger.info(f"Starting analysis for: {url}")
        
        # Clients are always initialized (in test mode if no keys)
        if not self.firecrawl_client:
            return False, "Firecrawl client initialization failed", None
        
        if not self.ai_client:
            return False, "AI client initialization failed", None
        
        if not self.config.is_profile_complete():
            logger.warning("User profile not complete")
        
        # Step 1: Scrape with Firecrawl
        success, content, metadata = self.firecrawl_client.scrape_url(url)
        
        if not success:
            logger.error(f"Scraping failed: {content}")
            return False, f"Scraping failed: {content}", None
        
        logger.info(f"Scraped {len(content)} characters")
        
        # Step 2: Get RAG context if knowledge base available
        rag_context = ""
        if self.knowledge_base:
            try:
                # Use scraped content as query to find relevant company knowledge
                search_query = f"{url} {content[:500]}"  # Use URL + content preview
                rag_context = self.knowledge_base.get_context_for_prompt(
                    query=search_query,
                    max_chunks=3
                )
                if rag_context:
                    logger.info("Retrieved RAG context from knowledge base")
                else:
                    logger.info("No relevant context found in knowledge base")
            except Exception as e:
                logger.warning(f"Error retrieving RAG context: {e}")
        
        # Step 3: Analyze with AI (with RAG context if available)
        user_profile = {
            'my_website': self.config.my_website,
            'my_value_proposition': self.config.my_value_proposition,
            'my_icp': self.config.my_icp,
            'knowledge_base_context': rag_context  # Add RAG context
        }
        
        ai_result = self.ai_client.analyze_lead(content, user_profile, url)
        
        if 'error' in ai_result:
            logger.error(f"AI analysis failed: {ai_result['error']}")
            return False, f"AI analysis failed: {ai_result['error']}", None
        
        # Step 3: Create Lead object
        try:
            lead = Lead.from_ai_analysis(
                url=url,
                ai_result=ai_result,
                scraped_content=content,
                metadata=metadata
            )
            
            logger.info(f"Lead created: {lead.company_name} (Score: {lead.lead_score})")
            
            return True, "Analysis complete", lead
            
        except Exception as e:
            logger.error(f"Failed to create lead: {e}", exc_info=True)
            return False, f"Error creating lead: {str(e)}", None
    
    def analyze_and_save(self, url: str) -> Tuple[bool, str, int]:
        """
        Analyze URL and save to database
        
        Args:
            url: URL to analyze
            
        Returns:
            Tuple of (success, message, lead_id)
        """
        success, message, lead = self.analyze_single_url(url)
        
        if not success:
            return False, message, None
        
        try:
            lead_id = self.data_manager.add_lead(lead)
            logger.info(f"Lead saved with ID: {lead_id}")
            return True, f"Lead #{lead_id} saved successfully", lead_id
            
        except Exception as e:
            logger.error(f"Failed to save lead: {e}")
            return False, f"Error saving lead: {str(e)}", None
    
    def analyze_bulk_urls(self, 
                          urls: list, 
                          delay: float = None) -> list[Dict]:
        """
        Analyze multiple URLs with rate limiting
        
        Args:
            urls: List of URLs to analyze
            delay: Delay between requests (uses config default if None)
            
        Returns:
            List of result dictionaries
        """
        if delay is None:
            delay = self.config.rate_limit_delay
        
        # Limit bulk size
        if len(urls) > Constants.MAX_BULK_URLS:
            logger.warning(f"Bulk request too large, limiting to {Constants.MAX_BULK_URLS}")
            urls = urls[:Constants.MAX_BULK_URLS]
        
        results = []
        
        for idx, url in enumerate(urls, 1):
            logger.info(f"Processing {idx}/{len(urls)}: {url}")
            
            success, message, lead_id = self.analyze_and_save(url)
            
            results.append({
                'url': url,
                'success': success,
                'message': message,
                'lead_id': lead_id
            })
            
            # Rate limiting
            if idx < len(urls):
                time.sleep(delay)
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"Bulk analysis complete: {successful}/{len(urls)} successful")
        
        return results
    
    def get_user_profile_dict(self) -> Dict:
        """Get user profile as dictionary"""
        return {
            'my_website': self.config.my_website,
            'my_value_proposition': self.config.my_value_proposition,
            'my_icp': self.config.my_icp
        }
