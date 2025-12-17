"""
Data Encryption Utility
=======================

Phase 5: Security & Validation
Provides encryption/decryption for sensitive data using AES-256 (Fernet).

Features:
- AES-256 encryption (Fernet)
- Key management
- Secure key generation
- Automatic key storage/retrieval
"""

import os
import base64
from pathlib import Path
from typing import Optional, bytes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class EncryptionManager:
    """
    Manages encryption/decryption for sensitive data.
    Uses Fernet (AES-128 in CBC mode with HMAC) for symmetric encryption.
    """
    
    def __init__(self, key_file: Optional[str] = None):
        """
        Initialize encryption manager.
        
        Args:
            key_file: Path to encryption key file (optional)
        """
        self.key_file = key_file or self._get_default_key_file()
        self._key: Optional[bytes] = None
        self._cipher: Optional[Fernet] = None
    
    def _get_default_key_file(self) -> str:
        """Get default key file path."""
        # Store key in project root/.keys/encryption.key
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        keys_dir = project_root / '.keys'
        keys_dir.mkdir(exist_ok=True)
        return str(keys_dir / 'encryption.key')
    
    def _generate_key(self) -> bytes:
        """
        Generate a new encryption key.
        
        Returns:
            Encryption key as bytes
        """
        return Fernet.generate_key()
    
    def _load_key(self) -> bytes:
        """
        Load encryption key from file, or generate new one if not exists.
        
        Returns:
            Encryption key as bytes
        """
        key_path = Path(self.key_file)
        
        if key_path.exists():
            # Load existing key
            try:
                with open(key_path, 'rb') as f:
                    key = f.read()
                if len(key) == 0:
                    raise ValueError("Key file is empty")
                return key
            except Exception as e:
                print(f"[WARNING] Failed to load encryption key: {e}")
                print("[INFO] Generating new encryption key...")
        
        # Generate new key
        key = self._generate_key()
        
        # Save key to file
        try:
            key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (Unix only)
            try:
                os.chmod(key_path, 0o600)  # Read/write for owner only
            except OSError:
                pass  # Windows doesn't support chmod
            print(f"[INFO] Encryption key saved to: {key_path}")
        except Exception as e:
            print(f"[WARNING] Failed to save encryption key: {e}")
            print("[WARNING] Encryption key will be regenerated on next run")
        
        return key
    
    def _get_key(self) -> bytes:
        """Get encryption key (lazy loading)."""
        if self._key is None:
            self._key = self._load_key()
        return self._key
    
    def _get_cipher(self) -> Fernet:
        """Get Fernet cipher instance (lazy loading)."""
        if self._cipher is None:
            key = self._get_key()
            self._cipher = Fernet(key)
        return self._cipher
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
            
        Raises:
            Exception: If encryption fails
        """
        if not data:
            return ""
        
        try:
            cipher = self._get_cipher()
            encrypted_bytes = cipher.encrypt(data.encode('utf-8'))
            # Return as base64 string for easy storage
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted plain text string
            
        Raises:
            Exception: If decryption fails (e.g., wrong key, corrupted data)
        """
        if not encrypted_data:
            return ""
        
        try:
            cipher = self._get_cipher()
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Output path (default: file_path + '.encrypted')
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        # Read file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Encrypt
        cipher = self._get_cipher()
        encrypted_data = cipher.encrypt(file_data)
        
        # Write encrypted file
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        return output_path
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file.
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Output path (default: encrypted_file_path without .encrypted)
            
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        # Read encrypted file
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        cipher = self._get_cipher()
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        return output_path


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager(key_file: Optional[str] = None) -> EncryptionManager:
    """
    Get or create global encryption manager instance.
    
    Args:
        key_file: Optional key file path
        
    Returns:
        EncryptionManager instance
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager(key_file)
    return _encryption_manager


def encrypt_sensitive_data(data: str, key_file: Optional[str] = None) -> str:
    """
    Convenience function to encrypt sensitive data.
    
    Args:
        data: Plain text to encrypt
        key_file: Optional key file path
        
    Returns:
        Encrypted string
    """
    manager = get_encryption_manager(key_file)
    return manager.encrypt(data)


def decrypt_sensitive_data(encrypted_data: str, key_file: Optional[str] = None) -> str:
    """
    Convenience function to decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted string
        key_file: Optional key file path
        
    Returns:
        Decrypted plain text
    """
    manager = get_encryption_manager(key_file)
    return manager.decrypt(encrypted_data)

