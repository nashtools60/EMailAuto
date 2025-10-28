import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_encryption_key():
    """
    Get or generate encryption key for password encryption
    Uses a fixed salt derived from DATABASE_URL for consistency
    Requires PGPASSWORD environment variable for secure key derivation
    """
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required for encryption")
    
    # Get key material - must be from PGPASSWORD (set by Replit database)
    key_material = os.environ.get('PGPASSWORD')
    if not key_material:
        raise ValueError("PGPASSWORD environment variable is required for secure password encryption")
    
    salt = base64.urlsafe_b64decode(
        base64.urlsafe_b64encode(database_url.encode()[:16].ljust(16, b'0'))
    )
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(key_material.encode()))
    
    return key

def encrypt_password(password: str) -> str:
    """
    Encrypt a password for secure storage
    """
    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())
    return encrypted.decode()

def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt a password for use
    """
    key = get_encryption_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_password.encode())
    return decrypted.decode()
