"""
Data Manager Service
Handles lead data persistence with JSON storage
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

from src.config import LEADS_FILE, get_logger, AppConfig
from src.models.lead import Lead
from src.security import SecureConfigManager

logger = get_logger(__name__)


class DataManagerError(Exception):
    """Custom exception for data management errors"""
    pass


class DataManager:
    """Manages lead data persistence"""
    
    def __init__(self, data_file: Path = LEADS_FILE):
        """
        Initialize DataManager
        
        Args:
            data_file: Path to JSON data file
        """
        self.data_file = data_file
        self._ensure_file_exists()
        self._config_manager = SecureConfigManager()
        
        logger.info(f"DataManager initialized (file: {self.data_file})")
    
    def _ensure_file_exists(self):
        """Ensure data file and directory exist"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.data_file.exists():
            self.data_file.write_text('[]', encoding='utf-8')
            logger.info("Created new data file")
    
    def _get_test_leads(self) -> List[Lead]:
        """Generate consistent test leads for demonstration"""
        test_leads_data = [
            {
                'id': 9001,
                'company_name': 'TechFlow Solutions',
                'lead_score': 85,
                'industry': 'B2B SaaS',
                'url': 'https://techflow-solutions.com',
                'score_rationale': 'High growth potential with strong product-market fit in automation space',
                'key_insights': 'Recently raised Series B funding, expanding team by 40%',
                'fit_analysis': 'Perfect match for our automation solutions. Strong technical team with clear scaling needs.',
                'recommended_action': 'Qualified',
                'personalized_email': """Subject: Partnership Opportunity - Automating Your Workflow

Hi [Name],

I noticed TechFlow Solutions has been expanding rapidly in the B2B SaaS automation space. Your recent Series B funding and 40% team growth shows impressive momentum.

We help companies like yours streamline their operations through our automation platform. Given your focus on workflow efficiency, I believe there could be strong synergies.

Would you be open to a brief conversation about how we might support your continued growth?

Best regards,
[Your Name]""",
                'sms_draft': 'Hi [Name], congrats on your Series B! Would love to chat about automation solutions for TechFlow. 15 min call this week?',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'id': 9002,
                'company_name': 'DataSync Pro',
                'lead_score': 72,
                'industry': 'Data Analytics',
                'url': 'https://datasync-pro.com',
                'score_rationale': 'Good fit for enterprise clients, proven track record',
                'key_insights': 'Strong technical team, looking to expand market presence',
                'fit_analysis': 'Solid prospect with growth potential. Could benefit from our data integration solutions.',
                'recommended_action': 'Further Research',
                'personalized_email': """Subject: Data Integration Solutions for DataSync Pro

Hello [Name],

I came across DataSync Pro and was impressed by your real-time data integration platform. Your strong technical foundation positions you well in the growing data analytics market.

We work with similar companies to optimize their data workflows and scale their operations. I believe there might be valuable opportunities for collaboration.

Would you be interested in exploring how we could support your market expansion goals?

Best,
[Your Name]""",
                'sms_draft': 'Hi [Name], impressed by DataSync Pro! Quick question about your data integration needs - 10 min call?',
                'timestamp': (datetime.now() - timedelta(hours=5)).isoformat()
            },
            {
                'id': 9003,
                'company_name': 'CustomerFirst AI',
                'lead_score': 91,
                'industry': 'AI/ML',
                'url': 'https://customerfirst-ai.com',
                'score_rationale': 'Perfect ICP match with high growth trajectory and recent funding',
                'key_insights': 'AI-powered customer success platform, $10M ARR, Series A funded',
                'fit_analysis': 'Ideal customer profile match. High-growth AI company with proven revenue and funding.',
                'recommended_action': 'Qualified',
                'personalized_email': """Subject: Strategic Partnership - AI-Powered Customer Success

Dear [Name],

CustomerFirst AI caught my attention with your impressive $10M ARR and Series A funding. Your AI-powered customer success platform aligns perfectly with current market trends.

We specialize in helping AI companies scale their operations and optimize customer engagement. Given your rapid growth and innovative approach, I see significant potential for collaboration.

I'd love to discuss how we can support your continued success. Are you available for a brief call this week?

Best regards,
[Your Name]""",
                'sms_draft': 'Hi [Name], love what CustomerFirst AI is doing! Congrats on $10M ARR. Chat about scaling opportunities?',
                'timestamp': (datetime.now() - timedelta(hours=8)).isoformat()
            },
            {
                'id': 9004,
                'company_name': 'SecureVault Systems',
                'lead_score': 68,
                'industry': 'Cybersecurity',
                'url': 'https://securevault-systems.com',
                'score_rationale': 'Enterprise focus but smaller team, moderate growth potential',
                'key_insights': 'Specializes in compliance and security solutions for financial sector',
                'fit_analysis': 'Decent fit but may need more research to understand specific needs and budget.',
                'recommended_action': 'Further Research',
                'personalized_email': """Subject: Security & Compliance Solutions

Hi [Name],

I came across SecureVault Systems and your focus on enterprise security and compliance solutions, particularly for the financial sector.

We work with security-focused companies to enhance their operational efficiency while maintaining the highest security standards.

Would you be interested in a brief discussion about potential synergies?

Best,
[Your Name]""",
                'sms_draft': "Hi [Name], interested in SecureVault's compliance focus. Quick chat about security solutions?",
                'timestamp': (datetime.now() - timedelta(hours=12)).isoformat()
            },
            {
                'id': 9005,
                'company_name': 'GrowthMetrics',
                'lead_score': 79,
                'industry': 'Marketing Technology',
                'url': 'https://growthmetrics.com',
                'score_rationale': 'Growing martech company with good market position',
                'key_insights': 'Marketing analytics platform with focus on attribution and ROI tracking',
                'fit_analysis': 'Strong potential customer with clear value proposition and growing customer base.',
                'recommended_action': 'Qualified',
                'personalized_email': """Subject: Marketing Analytics & Growth Optimization

Hello [Name],

GrowthMetrics has impressed me with your marketing analytics and attribution platform. The focus on ROI tracking is exactly what many growing companies need.

We help martech companies like yours scale their operations and optimize their growth strategies.

I'd love to explore potential partnership opportunities. Are you available for a quick call?

Best regards,
[Your Name]""",
                'sms_draft': "Hi [Name], love GrowthMetrics' attribution focus! Chat about growth opportunities?",
                'timestamp': (datetime.now() - timedelta(hours=24)).isoformat()
            }
        ]
        
        return [Lead(**data) for data in test_leads_data]
    
    def _is_test_mode(self) -> bool:
        """Check if the application is in test mode"""
        try:
            config_dict = self._config_manager.load()
            config = AppConfig(**config_dict) if config_dict else AppConfig()
            return not config.has_valid_firecrawl_key() or not config.has_valid_ai_key()
        except Exception:
            # If we can't determine config, assume test mode
            return True
    
    def _clear_cache(self):
        """Clear cached leads data"""
        try:
            import streamlit as st
            cache_key = f"leads_data_{self.data_file}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            if f"{cache_key}_mtime" in st.session_state:
                del st.session_state[f"{cache_key}_mtime"]
        except Exception:
            # Session state might not be available in all contexts
            pass
    
    def load_all(self, use_cache: bool = True) -> List[Lead]:
        """
        Load all leads from storage. Returns test data when in test mode and no real leads exist.
        
        Args:
            use_cache: Whether to use cached data if available
        
        Returns:
            List of Lead objects
        """
        # Check cache first if enabled
        if use_cache:
            import streamlit as st
            cache_key = f"leads_data_{self.data_file}"
            
            # Check if data file modification time changed
            if self.data_file.exists():
                current_mtime = self.data_file.stat().st_mtime
                cached_mtime = st.session_state.get(f"{cache_key}_mtime", 0)
                
                if current_mtime == cached_mtime and cache_key in st.session_state:
                    logger.debug("Using cached leads data")
                    return st.session_state[cache_key]
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            leads = [Lead.from_dict(item) for item in data]
            
            # If no real leads and in test mode, return test data
            if len(leads) == 0 and self._is_test_mode():
                test_leads = self._get_test_leads()
                logger.info(f"Using test data: {len(test_leads)} test leads")
                leads = test_leads
            else:
                logger.info(f"Loaded {len(leads)} leads from storage")
            
            # Cache the results
            if use_cache:
                import streamlit as st
                cache_key = f"leads_data_{self.data_file}"
                st.session_state[cache_key] = leads
                st.session_state[f"{cache_key}_mtime"] = self.data_file.stat().st_mtime if self.data_file.exists() else 0
            
            return leads
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted data file: {e}")
            # Return test data if in test mode
            if self._is_test_mode():
                test_leads = self._get_test_leads()
                logger.info(f"Data file corrupted, using test data: {len(test_leads)} test leads")
                return test_leads
            return []
        except Exception as e:
            logger.error(f"Error loading leads: {e}", exc_info=True)
            # Return test data if in test mode
            if self._is_test_mode():
                test_leads = self._get_test_leads()
                logger.info(f"Error loading data, using test data: {len(test_leads)} test leads")
                return test_leads
            return []
    
    def save_all(self, leads: List[Lead]) -> bool:
        """
        Save all leads to storage
        
        Args:
            leads: List of Lead objects
            
        Returns:
            True if successful
        """
        try:
            # Convert to dictionaries
            data = [lead.to_dict() for lead in leads]
            
            # Atomic write with temp file
            temp_file = self.data_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Replace original file
            temp_file.replace(self.data_file)
            
            # Clear cache after data change
            self._clear_cache()
            
            logger.info(f"Saved {len(leads)} leads to storage")
            return True
            
        except Exception as e:
            logger.error(f"Error saving leads: {e}", exc_info=True)
            return False
    
    def add_lead(self, lead: Lead) -> int:
        """
        Add a new lead to storage
        
        Args:
            lead: Lead object to add
            
        Returns:
            ID of the added lead
        """
        leads = self.load_all()
        
        # Assign ID
        lead.id = len(leads) + 1
        lead.timestamp = datetime.now().isoformat()
        
        leads.append(lead)
        
        if self.save_all(leads):
            logger.info(f"Added lead #{lead.id}: {lead.company_name}")
            return lead.id
        else:
            raise DataManagerError("Failed to save lead")
    
    def get_lead(self, lead_id: int) -> Optional[Lead]:
        """
        Get lead by ID
        
        Args:
            lead_id: Lead ID
            
        Returns:
            Lead object or None
        """
        leads = self.load_all()
        
        for lead in leads:
            if lead.id == lead_id:
                return lead
        
        return None
    
    def update_lead(self, lead: Lead) -> bool:
        """
        Update existing lead
        
        Args:
            lead: Updated Lead object
            
        Returns:
            True if successful
        """
        if not lead.id:
            logger.error("Cannot update lead without ID")
            return False
        
        leads = self.load_all()
        
        # Find and replace
        for idx, existing in enumerate(leads):
            if existing.id == lead.id:
                leads[idx] = lead
                if self.save_all(leads):
                    logger.info(f"Updated lead #{lead.id}")
                    return True
                return False
        
        logger.warning(f"Lead #{lead.id} not found for update")
        return False
    
    def delete_lead(self, lead_id: int) -> bool:
        """
        Delete lead by ID
        
        Args:
            lead_id: Lead ID
            
        Returns:
            True if successful
        """
        leads = self.load_all()
        original_count = len(leads)
        
        leads = [l for l in leads if l.id != lead_id]
        
        if len(leads) < original_count:
            if self.save_all(leads):
                logger.info(f"Deleted lead #{lead_id}")
                return True
        
        logger.warning(f"Lead #{lead_id} not found for deletion")
        return False
    
    def get_qualified_leads(self, threshold: int = 70) -> List[Lead]:
        """Get leads above qualification threshold"""
        leads = self.load_all()
        qualified = [l for l in leads if l.lead_score >= threshold]
        logger.debug(f"Found {len(qualified)} qualified leads (threshold: {threshold})")
        return qualified
    
    def get_leads_by_industry(self, industry: str) -> List[Lead]:
        """Get leads filtered by industry"""
        leads = self.load_all()
        filtered = [l for l in leads if l.industry.lower() == industry.lower()]
        return filtered
    
    def get_statistics(self) -> dict:
        """
        Get statistics about stored leads
        
        Returns:
            Dictionary with statistics
        """
        leads = self.load_all()
        
        if not leads:
            return {
                'total': 0,
                'qualified': 0,
                'average_score': 0,
                'industries': {}
            }
        
        scores = [l.lead_score for l in leads]
        qualified = sum(1 for l in leads if l.is_qualified)
        
        # Count by industry
        industries = {}
        for lead in leads:
            industries[lead.industry] = industries.get(lead.industry, 0) + 1
        
        stats = {
            'total': len(leads),
            'qualified': qualified,
            'qualification_rate': (qualified / len(leads)) * 100,
            'average_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'industries': industries,
            'top_industry': max(industries, key=industries.get) if industries else None
        }
        
        logger.debug(f"Statistics: {stats['total']} leads, {stats['qualified']} qualified")
        return stats
    
    def export_to_dict_list(self) -> List[dict]:
        """Export all leads as list of dictionaries"""
        leads = self.load_all()
        return [lead.to_dict() for lead in leads]
    
    def backup(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create backup of data file
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            True if successful
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = self.data_file.with_suffix(f'.backup_{timestamp}.json')
            
            import shutil
            shutil.copy2(self.data_file, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
