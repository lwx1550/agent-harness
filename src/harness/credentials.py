import os
import tempfile
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet


class CredentialManager:
    def __init__(self, service: str = "agent-harness", storage_dir: Optional[str] = None):
        self.service = service
        self._keyring_available = self._check_keyring()
        self._storage_dir = storage_dir or os.path.join(tempfile.gettempdir(), "agent-harness", "credentials")

    def _check_keyring(self) -> bool:
        try:
            import keyring
            keyring.get_password(self.service, "_probe")
            return True
        except Exception:
            return False

    def store(self, key: str, value: str, master_password: Optional[str] = None) -> None:
        if self._keyring_available:
            import keyring
            keyring.set_password(self.service, key, value)
        else:
            self._store_encrypted(key, value, master_password or "default")

    def get(self, key: str, master_password: Optional[str] = None) -> Optional[str]:
        if self._keyring_available:
            import keyring
            return keyring.get_password(self.service, key)
        return self._get_encrypted(key, master_password or "default")

    def delete(self, key: str) -> None:
        if self._keyring_available:
            import keyring
            keyring.delete_password(self.service, key)
        else:
            self._delete_encrypted(key)

    def _store_encrypted(self, key: str, value: str, password: str) -> None:
        derived = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
        cipher = Fernet(derived)
        encrypted = cipher.encrypt(value.encode())
        os.makedirs(self._storage_dir, exist_ok=True)
        path = os.path.join(self._storage_dir, f"{key}.enc")
        with open(path, "wb") as f:
            f.write(encrypted)

    def _get_encrypted(self, key: str, password: str) -> Optional[str]:
        path = os.path.join(self._storage_dir, f"{key}.enc")
        if not os.path.exists(path):
            return None
        try:
            derived = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
            cipher = Fernet(derived)
            with open(path, "rb") as f:
                return cipher.decrypt(f.read()).decode()
        except Exception:
            return None

    def _delete_encrypted(self, key: str) -> None:
        path = os.path.join(self._storage_dir, f"{key}.enc")
        if os.path.exists(path):
            os.remove(path)

