"""
Encryption service for securing sensitive data like API keys
Uses Fernet symmetric encryption from cryptography library
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self, encryption_key: str = None):
        """
        Initialize encryption service with a key
        
        Args:
            encryption_key: Base encryption key (should be from environment variable)
                           If not provided, will use ENCRYPTION_KEY from env or generate one
        """
        # Get encryption key from parameter, environment, or generate new one
        self.master_key = encryption_key or os.getenv('ENCRYPTION_KEY')
        
        if not self.master_key:
            # Generate a new key if none exists (for development only)
            logger.warning("No ENCRYPTION_KEY found in environment. Generating a new one. "
                         "This should only happen in development. For production, set ENCRYPTION_KEY in environment.")
            self.master_key = Fernet.generate_key().decode()
        
        # Derive a Fernet key from the master key
        self.fernet = self._get_fernet_cipher()
    
    def _get_fernet_cipher(self) -> Fernet:
        """Generate a Fernet cipher from the master key"""
        # Use PBKDF2 to derive a proper Fernet key from the master key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'finq_salt_v1',  # Static salt (should be in env in production)
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Failed to encrypt data: {str(e)}")
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt an encrypted string
        
        Args:
            encrypted_text: Encrypted string to decrypt
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return ""
        
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt an API key for storage
        
        Args:
            api_key: API key to encrypt
            
        Returns:
            Encrypted API key
        """
        return self.encrypt(api_key)
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt an API key from storage
        
        Args:
            encrypted_key: Encrypted API key
            
        Returns:
            Decrypted API key
        """
        return self.decrypt(encrypted_key)


# Global instance (singleton pattern)
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get or create global encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
