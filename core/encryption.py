#!/usr/bin/env python3
"""
Encryption Service for AI Microscope Application
Handles data encryption for database and exports
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from utils.logger import log_info, log_error, log_warning


class EncryptionService:
    """Service for encrypting and decrypting data."""
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryption service.
        
        Args:
            key: Encryption key (generates new if None)
        """
        if key is None:
            key = self._generate_key()
        
        self.cipher = Fernet(key)
        log_info("Encryption service initialized")
    
    def _generate_key(self, password: Optional[str] = None) -> bytes:
        """Generate encryption key from password or random.
        
        Args:
            password: Password for key derivation (None for random)
            
        Returns:
            Encryption key
        """
        if password:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ai_microscope_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            # Generate random key
            key = Fernet.generate_key()
        
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data.
        
        Args:
            data: Plain text string
            
        Returns:
            Encrypted string (base64 encoded)
        """
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            log_error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data.
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Plain text string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            log_error(f"Decryption failed: {str(e)}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any], keys_to_encrypt: list) -> Dict[str, Any]:
        """Encrypt specific keys in a dictionary.
        
        Args:
            data: Dictionary to encrypt
            keys_to_encrypt: List of keys to encrypt
            
        Returns:
            Dictionary with encrypted values
        """
        encrypted = data.copy()
        for key in keys_to_encrypt:
            if key in encrypted and encrypted[key]:
                encrypted[key] = self.encrypt(str(encrypted[key]))
        return encrypted
    
    def decrypt_dict(self, data: Dict[str, Any], keys_to_decrypt: list) -> Dict[str, Any]:
        """Decrypt specific keys in a dictionary.
        
        Args:
            data: Dictionary to decrypt
            keys_to_decrypt: List of keys to decrypt
            
        Returns:
            Dictionary with decrypted values
        """
        decrypted = data.copy()
        for key in keys_to_decrypt:
            if key in decrypted and decrypted[key]:
                try:
                    decrypted[key] = self.decrypt(decrypted[key])
                except Exception:
                    # Keep original if decryption fails
                    pass
        return decrypted


class EncryptedSQLite:
    """SQLite database with field-level encryption."""
    
    def __init__(
        self,
        db_path: Path,
        encryption_service: EncryptionService,
        encrypted_columns: Optional[list] = None
    ):
        """Initialize encrypted SQLite connection.
        
        Args:
            db_path: Path to database file
            encryption_service: Encryption service instance
            encrypted_columns: List of columns to encrypt
        """
        self.db_path = Path(db_path)
        self.encryption_service = encryption_service
        self.encrypted_columns = encrypted_columns or [
            'patient_name',
            'patient_id',
            'notes'
        ]
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
    
    def execute(self, sql: str, params: tuple = (), encrypt: bool = True) -> sqlite3.Cursor:
        """Execute SQL with automatic encryption/decryption.
        
        Args:
            sql: SQL statement
            params: Parameters for SQL
            encrypt: Whether to encrypt parameters
            
        Returns:
            Cursor
        """
        if encrypt and params:
            # Encrypt sensitive parameters
            params = list(params)
            for i, value in enumerate(params):
                if isinstance(value, str):
                    params[i] = self.encryption_service.encrypt(value)
        
        return self.connection.execute(sql, tuple(params))
    
    def fetchone(self, sql: str, params: tuple = (), decrypt: bool = True) -> Optional[Dict[str, Any]]:
        """Fetch one row with automatic decryption.
        
        Args:
            sql: SQL statement
            params: Parameters for SQL
            decrypt: Whether to decrypt results
            
        Returns:
            Dictionary with row data or None
        """
        cursor = self.execute(sql, params, encrypt=False)
        row = cursor.fetchone()
        
        if row and decrypt:
            row_dict = dict(row)
            return self.encryption_service.decrypt_dict(row_dict, self.encrypted_columns)
        
        return dict(row) if row else None
    
    def fetchall(self, sql: str, params: tuple = (), decrypt: bool = True) -> list:
        """Fetch all rows with automatic decryption.
        
        Args:
            sql: SQL statement
            params: Parameters for SQL
            decrypt: Whether to decrypt results
            
        Returns:
            List of dictionaries with row data
        """
        cursor = self.execute(sql, params, encrypt=False)
        rows = cursor.fetchall()
        
        if decrypt:
            return [
                self.encryption_service.decrypt_dict(dict(row), self.encrypted_columns)
                for row in rows
            ]
        
        return [dict(row) for row in rows]
    
    def commit(self) -> None:
        """Commit transaction."""
        self.connection.commit()
    
    def close(self) -> None:
        """Close connection."""
        self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_encryption_key_from_env() -> Optional[bytes]:
    """Get encryption key from environment variable.
    
    Returns:
        Encryption key or None
    """
    key_str = os.environ.get('AI_MICROSCOPE_ENCRYPTION_KEY')
    if key_str:
        return key_str.encode()
    return None


def save_encryption_key(key: bytes, key_file: Path) -> None:
    """Save encryption key to file.
    
    Args:
        key: Encryption key
        key_file: Path to save key
    """
    key_file.parent.mkdir(parents=True, exist_ok=True)
    with open(key_file, 'wb') as f:
        f.write(key)
    log_info(f"Encryption key saved to {key_file}")


def load_encryption_key(key_file: Path) -> Optional[bytes]:
    """Load encryption key from file.
    
    Args:
        key_file: Path to key file
        
    Returns:
        Encryption key or None
    """
    if key_file.exists():
        with open(key_file, 'rb') as f:
            return f.read()
    return None
