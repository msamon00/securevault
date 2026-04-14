import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 600,000 is the OWASP recommended minimum for PBKDF2-HMAC-SHA256 as of 2023
PBKDF2_ITERATIONS = 600_000
KEY_LENGTH = 32  # 256 bits for AES-256
SALT_LENGTH = 32  # 256-bit salt
IV_LENGTH = 12   # 96-bit IV, standard for AES-GCM


def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit encryption key from the master password using PBKDF2-HMAC-SHA256.
    The same password + salt always produces the same key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(master_password.encode())


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return os.urandom(SALT_LENGTH)


def generate_iv() -> bytes:
    """Generate a cryptographically secure random IV for AES-GCM."""
    return os.urandom(IV_LENGTH)


def encrypt(plaintext: str, key: bytes) -> tuple[str, str]:
    """
    Encrypt plaintext using AES-256-GCM.
    Returns (ciphertext_b64, iv_b64).
    AES-GCM provides both confidentiality AND authenticity.
    """
    iv = generate_iv()
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext.encode(), None)
    return (
        base64.b64encode(ciphertext).decode(),
        base64.b64encode(iv).decode()
    )


def decrypt(ciphertext_b64: str, iv_b64: str, key: bytes) -> str:
    """
    Decrypt AES-256-GCM ciphertext.
    Raises an exception if the key is wrong or data has been tampered with.
    """
    ciphertext = base64.b64decode(ciphertext_b64.encode())
    iv = base64.b64decode(iv_b64.encode())
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return plaintext.decode()