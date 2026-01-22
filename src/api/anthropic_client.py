"""
Anthropic (Claude) API Client
Handles Anthropic API interactions for lead analysis
"""

import requests
import json
import re
from typing import Dict

from src.config import APIEndpoints, Constants, get_logger
from src.api.mock_data import MockDataGenerator

logger = get_logger(__name__)


class AnthropicError(Exception):
    """Custom exception for Anthropic API errors"""
    pass


class AnthropicClient:
    """Anthropic Claude API client for lead analysis"""
    
    def __init__(self, api_key: str, timeout: int = 60, test_mode: bool = False):
        """
        Initialize Anthropic client
        
        Args:
            api_key: Anthropic API key
            timeout: Request timeout in seconds
            test_mode: If True, return mock analysis instead of calling API
        """
        self.api_key = api_key
        self.timeout = timeout
        self.model = Constants.ANTHROPIC_MODEL
        self.test_mode = test_mode
        
        if test_mode:
            logger.info(f"Anthropic client initialized in TEST MODE (using mock analysis)")
        else:
            logger.info(f"Anthropic client initialized (model: {self.model})")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            'x-api-key': self.api_key,
            'anthropic-version': Constants.ANTHROPIC_VERSION,
            'content-type': 'application/json'
        }
    
    def analyze_lead(self, 
                     content: str, 
                     user_profile: Dict,
                     url: str) -> Dict:
        """
        Analyze lead using Anthropic Claude
        
        Args:
            content: Scraped markdown content
            user_profile: User's company profile
            url: URL being analyzed
            
        Returns:
            Analysis dictionary or error dict
        """
        logger.info(f"Analyzing lead with Claude: {url}")
        
        # Test mode - return mock analysis
        if self.test_mode:
            logger.info(f"Test mode: Returning mock analysis for {url}")
            return MockDataGenerator.get_mock_lead_analysis(content, user_profile, url)
        
        # Prepare prompt
        prompt = self._build_prompt(content, user_profile, url)
        
        try:
            payload = {
                'model': self.model,
                'max_tokens': 2048,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            response = requests.post(
                APIEndpoints.ANTHROPIC_MESSAGES,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                content_text = data['content'][0]['text']
                
                # Extract JSON from response (Claude sometimes adds text)
                result = self._extract_json(content_text)
                
                if result:
                    logger.info(f"Claude analysis complete (score: {result.get('lead_score', 'N/A')})")
                    return result
                else:
                    logger.error("Failed to extract JSON from Claude response")
                    return {"error": "Invalid response format from Claude"}
            
            elif response.status_code == 401:
                logger.error("Anthropic authentication failed")
                return {"error": "Invalid Anthropic API key"}
            
            elif response.status_code == 429:
                logger.warning("Anthropic rate limit exceeded")
                return {"error": "Anthropic rate limit exceeded - try again later"}
            
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Bad request')
                logger.error(f"Anthropic bad request: {error_msg}")
                return {"error": f"Anthropic error: {error_msg}"}
            
            else:
                logger.error(f"Anthropic API error: {response.status_code}")
                return {"error": f"Anthropic API error: {response.status_code}"}
        
        except requests.exceptions.Timeout:
            logger.error("Anthropic request timeout")
            return {"error": "Anthropic request timeout"}
        
        except Exception as e:
            logger.error(f"Anthropic analysis error: {e}", exc_info=True)
            return {"error": f"Anthropic error: {str(e)}"}
    
    def _build_prompt(self, content: str, user_profile: Dict, url: str) -> str:
        """Build analysis prompt with optional RAG context"""
        # Truncate content if too long
        max_length = Constants.MAX_CONTENT_LENGTH
        if len(content) > max_length:
            content = content[:max_length]
            logger.debug(f"Content truncated to {max_length} characters")
        
        # Check for RAG context
        rag_context = user_profile.get('knowledge_base_context', '')
        
        # Build base prompt
        prompt = f"""You are an expert B2B lead qualification analyst. Analyze the following company website content and score it as a potential lead.

USER PROFILE (Your Company):
- Website: {user_profile.get('my_website', 'N/A')}
- Value Proposition: {user_profile.get('my_value_proposition', 'N/A')}
- Ideal Customer Profile: {user_profile.get('my_icp', 'N/A')}
"""
        
        # Add RAG context if available
        if rag_context:
            prompt += f"""
COMPANY KNOWLEDGE BASE (use this to inform your analysis):
{rag_context}

"""
        
        # Add website content
        prompt += f"""
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
    "personalized_email": "<draft a personalized outreach email referencing specific content from their website{' and our company knowledge' if rag_context else ''}>",
    "sms_draft": "<draft a short SMS message (max 160 chars)>",
    "recommended_action": "<Qualified/Disqualified/Further Research>"
}}

Be specific and reference actual content found on their website{' and use insights from our company knowledge base to personalize the outreach' if rag_context else ''}.

IMPORTANT: Respond ONLY with valid JSON, no other text before or after."""
        
        return prompt
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from Claude's response"""
        try:
            # First try: parse directly
            return json.loads(text)
        except json.JSONDecodeError:
            # Second try: extract JSON from text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        
        logger.error("Could not extract valid JSON from response")
        return {}
