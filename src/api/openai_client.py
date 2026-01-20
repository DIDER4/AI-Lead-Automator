"""
OpenAI API Client
Handles OpenAI API interactions for lead analysis
"""

import requests
import json
from typing import Dict, Optional

from src.config import APIEndpoints, Constants, get_logger
from src.api.mock_data import MockDataGenerator

logger = get_logger(__name__)


class OpenAIError(Exception):
    """Custom exception for OpenAI API errors"""
    pass


class OpenAIClient:
    """OpenAI API client for lead analysis"""
    
    def __init__(self, api_key: str, timeout: int = 60, test_mode: bool = False):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            timeout: Request timeout in seconds
            test_mode: If True, return mock analysis instead of calling API
        """
        self.api_key = api_key
        self.timeout = timeout
        self.model = Constants.OPENAI_MODEL
        self.test_mode = test_mode
        
        if test_mode:
            logger.info(f"OpenAI client initialized in TEST MODE (using mock analysis)")
        else:
            logger.info(f"OpenAI client initialized (model: {self.model})")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def analyze_lead(self, 
                     content: str, 
                     user_profile: Dict,
                     url: str) -> Dict:
        """
        Analyze lead using OpenAI
        
        Args:
            content: Scraped markdown content
            user_profile: User's company profile
            url: URL being analyzed
            
        Returns:
            Analysis dictionary or error dict
        """
        logger.info(f"Analyzing lead with OpenAI: {url}")
        
        # Test mode - return mock analysis
        if self.test_mode:
            logger.info(f"Test mode: Returning mock analysis for {url}")
            return MockDataGenerator.get_mock_lead_analysis(content, user_profile, url)
        
        # Prepare prompt
        prompt = self._build_prompt(content, user_profile, url)
        
        try:
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert B2B lead analyst. Always respond with valid JSON.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 2000,
                'response_format': {'type': 'json_object'}
            }
            
            response = requests.post(
                APIEndpoints.OPENAI_CHAT,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                content_text = data['choices'][0]['message']['content']
                
                # Parse JSON response
                result = json.loads(content_text)
                logger.info(f"OpenAI analysis complete (score: {result.get('lead_score', 'N/A')})")
                return result
            
            elif response.status_code == 401:
                logger.error("OpenAI authentication failed")
                return {"error": "Invalid OpenAI API key"}
            
            elif response.status_code == 429:
                logger.warning("OpenAI rate limit exceeded")
                return {"error": "OpenAI rate limit exceeded - try again later"}
            
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Bad request')
                logger.error(f"OpenAI bad request: {error_msg}")
                return {"error": f"OpenAI error: {error_msg}"}
            
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return {"error": f"OpenAI API error: {response.status_code}"}
        
        except requests.exceptions.Timeout:
            logger.error("OpenAI request timeout")
            return {"error": "OpenAI request timeout"}
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return {"error": "Invalid JSON response from OpenAI"}
        
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}", exc_info=True)
            return {"error": f"OpenAI error: {str(e)}"}
    
    def _build_prompt(self, content: str, user_profile: Dict, url: str) -> str:
        """Build analysis prompt"""
        # Truncate content if too long
        max_length = Constants.MAX_CONTENT_LENGTH
        if len(content) > max_length:
            content = content[:max_length]
            logger.debug(f"Content truncated to {max_length} characters")
        
        prompt = f"""You are an expert B2B lead qualification analyst. Analyze the following company website content and score it as a potential lead.

USER PROFILE (Your Company):
- Website: {user_profile.get('my_website', 'N/A')}
- Value Proposition: {user_profile.get('my_value_proposition', 'N/A')}
- Ideal Customer Profile: {user_profile.get('my_icp', 'N/A')}

COMPANY WEBSITE CONTENT (scraped from {url}):
{content}

Please provide a detailed analysis in the following JSON format:
{{
    "lead_score": <integer 0-100>,
    "score_rationale": "<detailed explanation of the score>",
    "company_name": "<extracted company name>",
    "industry": "<identified industry>",
    "key_insights": "<3-5 key insights about the company>",
    "fit_analysis": "<why they are/aren't a good fit for our ICP>",
    "personalized_email": "<draft a personalized outreach email referencing specific content from their website>",
    "sms_draft": "<draft a short SMS message (max 160 chars)>",
    "recommended_action": "<Qualified/Disqualified/Further Research>"
}}

Be specific and reference actual content found on their website."""
        
        return prompt
    

