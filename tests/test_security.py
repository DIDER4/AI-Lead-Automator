"""
Test Security Module
Unit tests for encryption and validation
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.security import (
    KeyManager,
    SecureConfigManager,
    EncryptionError,
    InputValidator,
    ValidationError,
    hash_api_key,
    mask_api_key
)


class TestKeyManager:
    """Test encryption key management"""
    
    def test_key_generation(self):
        """Test that key is generated on first use"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_file = Path(tmpdir) / "test.key"
            km = KeyManager(key_file)
            
            assert key_file.exists()
            assert len(key_file.read_bytes()) > 0
    
    def test_key_persistence(self):
        """Test that same key is used across instances"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_file = Path(tmpdir) / "test.key"
            
            km1 = KeyManager(key_file)
            key1 = key_file.read_bytes()
            
            km2 = KeyManager(key_file)
            key2 = key_file.read_bytes()
            
            assert key1 == key2
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(Path(tmpdir) / "test.key")
            
            data = {'test': 'value', 'number': 42}
            encrypted = km.encrypt_dict(data)
            decrypted = km.decrypt_dict(encrypted)
            
            assert decrypted == data
    
    def test_invalid_decryption(self):
        """Test that invalid data raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(Path(tmpdir) / "test.key")
            
            with pytest.raises(EncryptionError):
                km.decrypt_dict(b'invalid_data')


class TestInputValidator:
    """Test input validation"""
    
    def test_valid_url(self):
        """Test valid URL validation"""
        valid, result = InputValidator.validate_url("https://www.example.com")
        assert valid
        assert result == "https://www.example.com"
    
    def test_url_with_missing_protocol(self):
        """Test URL without protocol gets https:// added"""
        valid, result = InputValidator.validate_url("example.com")
        assert valid
        assert result == "https://example.com"
    
    def test_invalid_url(self):
        """Test invalid URL validation"""
        valid, _ = InputValidator.validate_url("not a url")
        assert not valid
    
    def test_localhost_blocked(self):
        """Test that localhost is blocked"""
        valid, msg = InputValidator.validate_url("http://localhost:8000")
        assert not valid
        assert "localhost" in msg.lower()
    
    def test_valid_api_key(self):
        """Test valid API key"""
        valid, _ = InputValidator.validate_api_key("sk-1234567890abcdef")
        assert valid
    
    def test_short_api_key(self):
        """Test that short API keys are rejected"""
        valid, msg = InputValidator.validate_api_key("short")
        assert not valid
        assert "short" in msg.lower()
    
    def test_sanitize_text(self):
        """Test text sanitization"""
        dirty = "<script>alert('xss')</script>"
        clean = InputValidator.sanitize_text(dirty)
        assert "<script>" not in clean
        assert "&lt;script&gt;" in clean
    
    def test_validate_score(self):
        """Test score validation"""
        assert InputValidator.validate_score(50)[0]
        assert InputValidator.validate_score(0)[0]
        assert InputValidator.validate_score(100)[0]
        assert not InputValidator.validate_score(-1)[0]
        assert not InputValidator.validate_score(101)[0]


class TestSecurityHelpers:
    """Test security helper functions"""
    
    def test_hash_api_key(self):
        """Test API key hashing"""
        hash1 = hash_api_key("test_key_123")
        hash2 = hash_api_key("test_key_123")
        
        # Same input = same hash
        assert hash1 == hash2
        
        # Hash is short
        assert len(hash1) == 8
        
        # Different input = different hash
        hash3 = hash_api_key("different_key")
        assert hash1 != hash3
    
    def test_mask_api_key(self):
        """Test API key masking"""
        masked = mask_api_key("sk-1234567890abcdef")
        assert "sk-1" in masked
        assert "cdef" in masked
        assert "..." in masked
        assert "567890" not in masked


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
