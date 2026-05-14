"""Encryption utility for sensitive API credentials"""

import os
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("encryption")

# Default static key for testing/development if not provided in environment
DEFAULT_KEY = b"kSlE847u5sS2R8X76gP0T80wS1hRzWqB6e8K1s6z75k="


def get_cipher() -> Fernet:
    """Get Fernet cipher instance based on configured key"""
    key_str = getattr(settings, "ENCRYPTION_KEY", None)
    if not key_str:
        key = DEFAULT_KEY
    else:
        try:
            # Ensure key is bytes
            key = key_str.encode() if isinstance(key_str, str) else key_str
            # Test if valid fernet key length/format
            Fernet(key)
        except Exception:
            logger.warning("Configured ENCRYPTION_KEY is invalid for Fernet. Using default/fallback key.")
            key = DEFAULT_KEY
    return Fernet(key)


def encrypt_credential(value: str) -> str:
    """Encrypt a plain text string credential"""
    if not value:
        return value
    # Avoid double encryption if already prefixed
    if value.startswith("enc:"):
        return value
    try:
        cipher = get_cipher()
        encrypted_bytes = cipher.encrypt(value.encode())
        return f"enc:{encrypted_bytes.decode()}"
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return value


def decrypt_credential(value: str) -> str:
    """Decrypt an encrypted string credential. Returns original if not encrypted."""
    if not value:
        return value
    
    # Check if it has our encrypted prefix
    if value.startswith("enc:"):
        actual_value = value[4:]
    else:
        # Might be plain text from test cases or old DB records
        actual_value = value
        
    try:
        cipher = get_cipher()
        decrypted_bytes = cipher.decrypt(actual_value.encode())
        return decrypted_bytes.decode()
    except (InvalidToken, Exception):
        # Gracefully fall back to plain text for backward compatibility with tests/old records
        return value
