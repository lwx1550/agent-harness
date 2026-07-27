from harness.credentials import CredentialManager


def test_store_and_retrieve():
    cm = CredentialManager(service="test-agent-harness")
    # Force encrypted fallback since sandbox lacks keyring support
    cm._keyring_available = False
    cm.store("test_key", "test_value")
    value = cm.get("test_key")
    assert value == "test_value"
    cm.delete("test_key")
    assert cm.get("test_key") is None


def test_nonexistent_key():
    cm = CredentialManager(service="test-agent-harness")
    cm._keyring_available = False
    assert cm.get("nonexistent") is None


def test_encrypted_fallback():
    cm = CredentialManager(service="test-agent-encrypted")
    cm._keyring_available = False
    cm.store("secret", "my-api-key-12345", master_password="test-password")
    value = cm.get("secret", master_password="test-password")
    assert value == "my-api-key-12345"
    cm.delete("secret")
    assert cm.get("secret") is None

