"""
Data Manager Service
Handles lead data persistence with JSON storage
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.config import LEADS_FILE, get_logger
from src.models.lead import Lead

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
        
        logger.info(f"DataManager initialized (file: {self.data_file})")
    
    def _ensure_file_exists(self):
        """Ensure data file and directory exist"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.data_file.exists():
            self.data_file.write_text('[]', encoding='utf-8')
            logger.info("Created new data file")
    
    def load_all(self) -> List[Lead]:
        """
        Load all leads from storage
        
        Returns:
            List of Lead objects
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            leads = [Lead.from_dict(item) for item in data]
            logger.info(f"Loaded {len(leads)} leads from storage")
            return leads
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted data file: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading leads: {e}", exc_info=True)
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
