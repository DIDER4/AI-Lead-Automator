"""
Lead Data Model
Defines the structure for lead data with validation
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict
import json

from src.config import Constants, get_logger
from src.security.validators import InputValidator

logger = get_logger(__name__)


@dataclass
class Lead:
    """Lead data model with validation"""
    
    # Required fields
    url: str
    company_name: str
    lead_score: int
    
    # Analysis fields
    industry: str = "Unknown"
    score_rationale: str = ""
    key_insights: str = ""
    fit_analysis: str = ""
    personalized_email: str = ""
    sms_draft: str = ""
    recommended_action: str = "Further Research"
    
    # Metadata
    scraped_content: str = ""
    metadata: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validate fields after initialization"""
        # Validate URL
        is_valid, _ = InputValidator.validate_url(self.url)
        if not is_valid:
            logger.warning(f"Invalid URL in lead: {self.url}")
        
        # Validate score
        is_valid, msg = InputValidator.validate_score(self.lead_score)
        if not is_valid:
            raise ValueError(f"Invalid lead score: {msg}")
        
        # Sanitize text fields
        self.company_name = InputValidator.sanitize_text(self.company_name, max_length=200)
        self.industry = InputValidator.sanitize_text(self.industry, max_length=100)
        
        # Validate recommended action
        valid_actions = ["Qualified", "Disqualified", "Further Research"]
        if self.recommended_action not in valid_actions:
            logger.warning(f"Invalid recommended_action: {self.recommended_action}")
            self.recommended_action = "Further Research"
    
    @property
    def is_qualified(self) -> bool:
        """Check if lead meets qualification threshold"""
        return self.lead_score >= Constants.QUALIFIED_SCORE
    
    @property
    def qualification_status(self) -> str:
        """Get qualification status label"""
        if self.lead_score >= 80:
            return "🔥 Hot Lead"
        elif self.lead_score >= Constants.QUALIFIED_SCORE:
            return "✅ Qualified"
        elif self.lead_score >= Constants.WARM_SCORE:
            return "⚠️ Warm Lead"
        else:
            return "❄️ Cold Lead"
    
    @property
    def score_color(self) -> str:
        """Get color for score display"""
        if self.lead_score >= 80:
            return "green"
        elif self.lead_score >= Constants.QUALIFIED_SCORE:
            return "blue"
        elif self.lead_score >= Constants.WARM_SCORE:
            return "orange"
        else:
            return "red"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Lead':
        """Create Lead from dictionary"""
        # Filter only known fields
        known_fields = {
            'url', 'company_name', 'lead_score', 'industry',
            'score_rationale', 'key_insights', 'fit_analysis',
            'personalized_email', 'sms_draft', 'recommended_action',
            'scraped_content', 'metadata', 'timestamp', 'id'
        }
        
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_ai_analysis(cls, 
                         url: str, 
                         ai_result: Dict, 
                         scraped_content: str = "",
                         metadata: Dict = None) -> 'Lead':
        """
        Create Lead from AI analysis result
        
        Args:
            url: Original URL
            ai_result: Dictionary from AI analysis
            scraped_content: Raw scraped content
            metadata: Additional metadata
            
        Returns:
            Lead instance
        """
        return cls(
            url=url,
            company_name=ai_result.get('company_name', 'Unknown'),
            lead_score=ai_result.get('lead_score', 0),
            industry=ai_result.get('industry', 'Unknown'),
            score_rationale=ai_result.get('score_rationale', ''),
            key_insights=ai_result.get('key_insights', ''),
            fit_analysis=ai_result.get('fit_analysis', ''),
            personalized_email=ai_result.get('personalized_email', ''),
            sms_draft=ai_result.get('sms_draft', ''),
            recommended_action=ai_result.get('recommended_action', 'Further Research'),
            scraped_content=scraped_content[:500],  # Store first 500 chars
            metadata=metadata or {}
        )
    
    def __repr__(self) -> str:
        return f"<Lead {self.id}: {self.company_name} (Score: {self.lead_score})>"
    
    def __str__(self) -> str:
        return f"{self.company_name} - Score: {self.lead_score} - {self.qualification_status}"
