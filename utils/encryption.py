from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional

class EncryptionManager:
    """
    Manager for field-level encryption of sensitive PII data.
    Uses Fernet (symmetric encryption) with key derivation.
    """
    
    def __init__(self):
        """
        Initialize encryption manager.
        The encryption key should be stored securely (e.g., Azure Key Vault, AWS KMS).
        For development, we use an environment variable.
        """
        self._master_key = os.getenv("ENCRYPTION_MASTER_KEY")
        
        if not self._master_key:
            # Generate a new key if not exists (for development only)
            self._master_key = Fernet.generate_key().decode()
            print("WARNING: Generated new encryption key. Set ENCRYPTION_MASTER_KEY in production!")
        
        if isinstance(self._master_key, str):
            self._master_key = self._master_key.encode()
        
        self._cipher = Fernet(self._master_key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string value.
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not data:
            return data
        
        try:
            encrypted_data = self._cipher.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt an encrypted string value.
        
        Args:
            encrypted_data: Base64-encoded encrypted string
            
        Returns:
            Decrypted plain text string
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            decrypted_data = self._cipher.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing data
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except Exception:
                    # If decryption fails, keep original value (might not be encrypted)
                    pass
        
        return decrypted_data
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key.
        Use this to create a master key for production.
        
        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
        """
        Derive an encryption key from a password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if None)
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), base64.b64encode(salt).decode()


class EncryptedField:
    """
    SQLAlchemy custom type for encrypted fields.
    Automatically encrypts/decrypts data when reading/writing to database.
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database"""
        if value is not None:
            return self.encryption_manager.encrypt(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt value when reading from database"""
        if value is not None:
            return self.encryption_manager.decrypt(value)
        return value


# Singleton instance
_encryption_manager = None

def get_encryption_manager() -> EncryptionManager:
    """
    Get singleton instance of EncryptionManager.
    """
    global _encryption_manager
    
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    
    return _encryption_manager


# Convenience functions
def encrypt_value(value: str) -> str:
    """Encrypt a single value"""
    return get_encryption_manager().encrypt(value)


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a single value"""
    return get_encryption_manager().decrypt(encrypted_value)


def encrypt_sensitive_data(data: dict, sensitive_fields: list = None) -> dict:
    """
    Encrypt sensitive fields in user data.
    
    Default sensitive fields: ssn, phone, address, date_of_birth, medical_record_number
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'ssn',
            'phone',
            'address',
            'date_of_birth',
            'medical_record_number',
            'insurance_number'
        ]
    
    return get_encryption_manager().encrypt_dict(data, sensitive_fields)


def decrypt_sensitive_data(encrypted_data: dict, sensitive_fields: list = None) -> dict:
    """
    Decrypt sensitive fields in user data.
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'ssn',
            'phone',
            'address',
            'date_of_birth',
            'medical_record_number',
            'insurance_number'
        ]
    
    return get_encryption_manager().decrypt_dict(encrypted_data, sensitive_fields)


def encrypt_data(data: str) -> str:
    """
    Encrypt a string value.
    
    Args:
        data: Plain text string to encrypt
        
    Returns:
        Encrypted string
    """
    return get_encryption_manager().encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt an encrypted string value.
    
    Args:
        encrypted_data: Encrypted string
        
    Returns:
        Decrypted plain text string
    """
    return get_encryption_manager().decrypt(encrypted_data)

