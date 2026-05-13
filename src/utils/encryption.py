"""Encryption utilities for secure credential storage"""

from cryptography.fernet import Fernet
from typing import Optional
import os
from src.utils.logger import get_logger

logger = get_logger("encryption")


class CredentialEncryption:
    """Handle encryption/decryption of sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize with encryption key
        If not provided, will look for ENCRYPTION_KEY env var
        """
        if encryption_key:
            self.key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        else:
            key_from_env = os.getenv("ENCRYPTION_KEY")
            if not key_from_env:
                logger.warning("No encryption key provided! Generating new one...")
                self.key = Fernet.generate_key()
                logger.info(f"Generated encryption key: {self.key.decode()}")
                logger.warning("Store this key in ENCRYPTION_KEY environment variable!")
            else:
                self.key = key_from_env.encode() if isinstance(key_from_env, str) else key_from_env
        
        self.cipher = Fernet(self.key)
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string
        Returns: encrypted string (base64)
        """
        try:
            if isinstance(plaintext, str):
                plaintext = plaintext.encode()
            encrypted = self.cipher.encrypt(plaintext)
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string
        Returns: decrypted string
        """
        try:
            if isinstance(ciphertext, str):
                ciphertext = ciphertext.encode()
            decrypted = self.cipher.decrypt(ciphertext)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise


# Global encryption instance
_encryption: Optional[CredentialEncryption] = None


def get_encryption() -> CredentialEncryption:
    """Get or create global encryption instance"""
    global _encryption
    if _encryption is None:
        _encryption = CredentialEncryption()
    return _encryption


def encrypt_credential(credential: str) -> str:
    """Convenience function to encrypt credential"""
    return get_encryption().encrypt(credential)


def decrypt_credential(encrypted: str) -> str:
    """Convenience function to decrypt credential"""
    return get_encryption().decrypt(encrypted)
