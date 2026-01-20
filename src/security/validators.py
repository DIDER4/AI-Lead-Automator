"""
Security Module - Input Validation
Validates and sanitizes user inputs to prevent security vulnerabilities
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse
import html

from src.config import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Secure input validation"""
    
    # Patterns
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Dangerous patterns for XSS/injection prevention
    DANGEROUS_PATTERNS = [
        re.compile(r'<script', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onerror, etc.
        re.compile(r'<iframe', re.IGNORECASE),
    ]
    
    @staticmethod
    def validate_url(url: str, require_https: bool = False) -> Tuple[bool, str]:
        """
        Validate URL format and safety
        
        Args:
            url: URL to validate
            require_https: If True, only allow HTTPS URLs
            
        Returns:
            Tuple of (is_valid, error_message or cleaned_url)
        """
        if not url or not isinstance(url, str):
            return False, "URL is empty or invalid type"
        
        # Trim whitespace
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Check pattern
        if not InputValidator.URL_PATTERN.match(url):
            return False, "Invalid URL format"
        
        # Parse URL
        try:
            parsed = urlparse(url)
            
            # Check for HTTPS if required
            if require_https and parsed.scheme != 'https':
                return False, "Only HTTPS URLs are allowed"
            
            # Check for suspicious patterns
            if any(pattern.search(url) for pattern in InputValidator.DANGEROUS_PATTERNS):
                logger.warning(f"Dangerous pattern detected in URL: {url}")
                return False, "URL contains potentially dangerous content"
            
            # Additional safety checks
            if parsed.hostname:
                # Block common malicious patterns
                blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
                if parsed.hostname.lower() in blocked_hosts:
                    return False, "Localhost URLs are not allowed"
            
            logger.debug(f"URL validated: {parsed.hostname}")
            return True, url
            
        except Exception as e:
            logger.error(f"URL parsing error: {e}")
            return False, f"URL parsing failed: {str(e)}"
    
    @staticmethod
    def validate_api_key(api_key: str, min_length: int = 10) -> Tuple[bool, str]:
        """
        Validate API key format
        
        Args:
            api_key: API key to validate
            min_length: Minimum required length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key or not isinstance(api_key, str):
            return False, "API key is empty"
        
        api_key = api_key.strip()
        
        if len(api_key) < min_length:
            return False, f"API key too short (minimum {min_length} characters)"
        
        # Check for whitespace (API keys shouldn't have spaces)
        if ' ' in api_key:
            return False, "API key contains invalid whitespace"
        
        # Check for common prefixes
        valid_prefixes = ['sk-', 'fc-', 'Bearer ', 'pk-']
        # Allow keys without prefix too
        
        logger.debug("API key format validated")
        return True, "Valid"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False, "Email is empty"
        
        email = email.strip().lower()
        
        if not InputValidator.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, email
    
    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text input to prevent XSS
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Escape HTML
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters")
        
        return text
    
    @staticmethod
    def validate_json_input(data: dict, required_keys: list) -> Tuple[bool, str]:
        """
        Validate JSON input has required keys
        
        Args:
            data: Dictionary to validate
            required_keys: List of required keys
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_score(score: int) -> Tuple[bool, str]:
        """Validate lead score is within valid range"""
        if not isinstance(score, int):
            return False, "Score must be an integer"
        
        if not 0 <= score <= 100:
            return False, "Score must be between 0 and 100"
        
        return True, "Valid"
    
    @staticmethod
    def validate_file_path(path: str, allowed_extensions: Optional[list] = None) -> Tuple[bool, str]:
        """
        Validate file path for security
        
        Args:
            path: File path to validate
            allowed_extensions: List of allowed extensions (e.g., ['.json', '.csv'])
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path:
            return False, "Path is empty"
        
        # Check for path traversal attempts
        if '..' in path:
            logger.warning(f"Path traversal attempt detected: {path}")
            return False, "Path traversal detected"
        
        # Check for absolute paths (security risk)
        if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
            return False, "Absolute paths not allowed"
        
        # Check extension if specified
        if allowed_extensions:
            if not any(path.endswith(ext) for ext in allowed_extensions):
                return False, f"File extension must be one of: {', '.join(allowed_extensions)}"
        
        return True, "Valid"


# Convenience functions
def is_valid_url(url: str) -> bool:
    """Quick URL validation check"""
    valid, _ = InputValidator.validate_url(url)
    return valid


def is_valid_api_key(api_key: str) -> bool:
    """Quick API key validation check"""
    valid, _ = InputValidator.validate_api_key(api_key)
    return valid


def sanitize(text: str) -> str:
    """Quick text sanitization"""
    return InputValidator.sanitize_text(text)
