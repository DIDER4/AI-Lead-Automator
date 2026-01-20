"""
Security Module - Encryption and Key Management
Implements Fernet encryption for secure API key storage
"""

from cryptography.fernet import Fernet, InvalidToken
import json
from pathlib import Path
from typing import Dict, Optional
import secrets
import hashlib

from src.config import KEY_FILE, CONFIG_FILE, get_logger

logger = get_logger(__name__)


class EncryptionError(Exception):
    """Custom exception for encryption errors"""
    pass


class KeyManager:
    """Secure key management with Fernet encryption"""
    
    def __init__(self, key_file: Path = KEY_FILE):
        self.key_file = key_file
        self._cipher: Optional[Fernet] = None
    
    def _get_or_create_key(self) -> bytes:
        """Generate or load encryption key"""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                # Validate key format
                Fernet(key)  # Will raise if invalid
                logger.info("Loaded existing encryption key")
                return key
            except Exception as e:
                logger.error(f"Invalid encryption key file: {e}")
                raise EncryptionError(f"Corrupt encryption key: {e}")
        else:
            # Generate new key
            key = Fernet.generate_key()
            try:
                # Write with restricted permissions
                self.key_file.touch(mode=0o600)  # Owner read/write only
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                logger.info("Generated new encryption key")
                return key
            except Exception as e:
                logger.error(f"Failed to create key file: {e}")
                raise EncryptionError(f"Cannot create key file: {e}")
    
    @property
    def cipher(self) -> Fernet:
        """Get Fernet cipher instance (lazy loading)"""
        if self._cipher is None:
            key = self._get_or_create_key()
            self._cipher = Fernet(key)
        return self._cipher
    
    def encrypt_dict(self, data: Dict) -> bytes:
        """
        Encrypt dictionary data
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted bytes
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            encrypted = self.cipher.encrypt(json_data.encode('utf-8'))
            logger.debug("Data encrypted successfully")
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Encryption failed: {e}")
    
    def decrypt_dict(self, encrypted_data: bytes) -> Dict:
        """
        Decrypt data back to dictionary
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted dictionary
            
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_data)
            data = json.loads(decrypted.decode('utf-8'))
            logger.debug("Data decrypted successfully")
            return data
        except InvalidToken:
            logger.error("Decryption failed: Invalid token")
            raise EncryptionError("Invalid encryption key or corrupted data")
        except json.JSONDecodeError as e:
            logger.error(f"Decrypted data is not valid JSON: {e}")
            raise EncryptionError("Decrypted data is corrupted")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Decryption failed: {e}")
    
    def rotate_key(self, config_file: Path = CONFIG_FILE):
        """
        Rotate encryption key (re-encrypt existing data)
        
        WARNING: This is a sensitive operation. Backup data first!
        """
        logger.warning("Starting key rotation")
        
        # Load existing data with old key
        if config_file.exists():
            with open(config_file, 'rb') as f:
                encrypted_data = f.read()
            old_data = self.decrypt_dict(encrypted_data)
        else:
            old_data = {}
        
        # Generate new key
        old_key_file = self.key_file.with_suffix('.key.old')
        self.key_file.rename(old_key_file)
        logger.info("Backed up old key")
        
        # Reset cipher to generate new key
        self._cipher = None
        new_key = self._get_or_create_key()
        self._cipher = Fernet(new_key)
        
        # Re-encrypt data
        if old_data:
            encrypted_new = self.encrypt_dict(old_data)
            with open(config_file, 'wb') as f:
                f.write(encrypted_new)
        
        logger.info("Key rotation completed successfully")


class SecureConfigManager:
    """Manage encrypted configuration"""
    
    def __init__(self, 
                 config_file: Path = CONFIG_FILE,
                 key_manager: Optional[KeyManager] = None):
        self.config_file = config_file
        self.key_manager = key_manager or KeyManager()
    
    def save(self, config: Dict) -> bool:
        """
        Save encrypted configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful
        """
        try:
            # Sanitize config (remove empty values)
            sanitized = {k: v for k, v in config.items() if v is not None}
            
            encrypted = self.key_manager.encrypt_dict(sanitized)
            
            # Atomic write with temp file
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'wb') as f:
                f.write(encrypted)
            
            # Rename to actual file (atomic on most systems)
            temp_file.replace(self.config_file)
            
            logger.info(f"Configuration saved successfully (keys: {list(sanitized.keys())})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load(self) -> Dict:
        """
        Load encrypted configuration
        
        Returns:
            Configuration dictionary (empty if not exists)
        """
        if not self.config_file.exists():
            logger.debug("Configuration file does not exist")
            return {}
        
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            config = self.key_manager.decrypt_dict(encrypted_data)
            logger.info(f"Configuration loaded (keys: {list(config.keys())})")
            return config
            
        except EncryptionError as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            return {}
    
    def delete(self) -> bool:
        """Delete configuration file"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
                logger.warning("Configuration file deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete configuration: {e}")
            return False


def hash_api_key(api_key: str) -> str:
    """
    Create a hash of API key for logging/debugging without exposing the key
    
    Args:
        api_key: The API key to hash
        
    Returns:
        Short hash string (first 8 chars of SHA256)
    """
    if not api_key:
        return "empty"
    hash_obj = hashlib.sha256(api_key.encode())
    return hash_obj.hexdigest()[:8]


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask API key for display
    
    Args:
        api_key: Full API key
        visible_chars: Number of characters to show at start/end
        
    Returns:
        Masked string like "sk-1234...abcd"
    """
    if not api_key or len(api_key) <= visible_chars * 2:
        return "****"
    
    return f"{api_key[:visible_chars]}...{api_key[-visible_chars:]}"
