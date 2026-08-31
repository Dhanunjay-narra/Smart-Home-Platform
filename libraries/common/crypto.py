import hashlib
import hmac
import secrets
from typing import Optional

def hash_password(password: str, salt: Optional[str] = None) -> str:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, original_hash = stored_hash.split("$", 1)
    test_hash = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return hmac.compare_digest(test_hash, original_hash)
