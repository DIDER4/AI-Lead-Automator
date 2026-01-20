"""
GDPR Compliance Utilities
Handles data sanitization for GDPR compliance
"""

import pandas as pd
import re
from typing import List

from src.config import Constants, get_logger

logger = get_logger(__name__)


class GDPRCompliance:
    """GDPR compliance utilities"""
    
    # Patterns for personal data detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
    
    # Personal data column names (case-insensitive)
    PERSONAL_COLUMNS = [
        'contact_name', 'first_name', 'last_name',
        'personal_mobile', 'mobile_phone', 'cell_phone',
        'direct_email', 'personal_email',
        'home_address', 'personal_address'
    ]
    
    @staticmethod
    def redact_dataframe(df: pd.DataFrame, 
                        redacted_text: str = Constants.REDACTED_TEXT) -> pd.DataFrame:
        """
        Redact personal data from DataFrame
        
        Args:
            df: DataFrame to redact
            redacted_text: Text to replace personal data with
            
        Returns:
            DataFrame with redacted personal data
        """
        df_safe = df.copy()
        
        # Redact known personal columns
        for col in df_safe.columns:
            col_lower = col.lower()
            
            # Check if column name indicates personal data
            if any(personal_col in col_lower for personal_col in GDPRCompliance.PERSONAL_COLUMNS):
                df_safe[col] = redacted_text
                logger.info(f"Redacted column: {col}")
        
        logger.info(f"GDPR redaction applied to DataFrame ({len(df_safe)} rows)")
        return df_safe
    
    @staticmethod
    def redact_text(text: str, 
                   redacted_text: str = "[REDACTED]") -> str:
        """
        Redact personal data from text
        
        Args:
            text: Text to redact
            redacted_text: Replacement text
            
        Returns:
            Text with redacted personal data
        """
        if not text:
            return text
        
        # Redact emails
        text = GDPRCompliance.EMAIL_PATTERN.sub(redacted_text, text)
        
        # Redact phone numbers
        text = GDPRCompliance.PHONE_PATTERN.sub(redacted_text, text)
        
        return text
    
    @staticmethod
    def is_gdpr_safe_column(column_name: str) -> bool:
        """Check if column name indicates GDPR-safe data"""
        col_lower = column_name.lower()
        
        # Safe columns (company data, not personal)
        safe_indicators = [
            'company', 'business', 'organization',
            'industry', 'sector', 'cvr', 'vat',
            'main_phone', 'general_email', 'info',
            'score', 'analysis', 'recommendation'
        ]
        
        return any(indicator in col_lower for indicator in safe_indicators)
    
    @staticmethod
    def get_gdpr_compliance_report(df: pd.DataFrame) -> dict:
        """
        Generate GDPR compliance report for DataFrame
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with compliance information
        """
        report = {
            'total_columns': len(df.columns),
            'personal_columns': [],
            'safe_columns': [],
            'unknown_columns': []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            if any(p in col_lower for p in GDPRCompliance.PERSONAL_COLUMNS):
                report['personal_columns'].append(col)
            elif GDPRCompliance.is_gdpr_safe_column(col):
                report['safe_columns'].append(col)
            else:
                report['unknown_columns'].append(col)
        
        report['compliance_percentage'] = (
            len(report['safe_columns']) / len(df.columns) * 100
            if len(df.columns) > 0 else 0
        )
        
        return report
    
    @staticmethod
    def create_gdpr_safe_export(leads: List[dict]) -> List[dict]:
        """
        Create GDPR-safe export of leads
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            List with redacted personal data
        """
        safe_leads = []
        
        for lead in leads:
            safe_lead = lead.copy()
            
            # Remove personal fields entirely
            personal_fields = [
                'contact_name', 'personal_mobile', 'direct_email',
                'scraped_content'  # May contain personal data
            ]
            
            for field in personal_fields:
                if field in safe_lead:
                    safe_lead[field] = Constants.REDACTED_TEXT
            
            safe_leads.append(safe_lead)
        
        logger.info(f"Created GDPR-safe export for {len(safe_leads)} leads")
        return safe_leads


def make_gdpr_safe(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function for GDPR redaction"""
    return GDPRCompliance.redact_dataframe(df)
