import pytest
from cryptography.fernet import Fernet, InvalidToken

from mcp_server.infrastructure.adapters.token_encryptor import TokenEncryptor


@pytest.mark.unit
class TestTokenEncryptor:
    def test_encrypt_decrypt_roundtrip(self):
        encryptor = TokenEncryptor(Fernet.generate_key().decode())

        ciphertext = encryptor.encrypt("my-secret-token")

        assert encryptor.decrypt(ciphertext) == "my-secret-token"

    def test_ciphertext_differs_from_plaintext(self):
        encryptor = TokenEncryptor(Fernet.generate_key().decode())

        ciphertext = encryptor.encrypt("my-secret-token")

        assert ciphertext != "my-secret-token"

    def test_different_ciphertexts_for_same_plaintext(self):
        encryptor = TokenEncryptor(Fernet.generate_key().decode())

        first = encryptor.encrypt("my-secret-token")
        second = encryptor.encrypt("my-secret-token")

        assert first != second

    def test_invalid_key_raises(self):
        with pytest.raises(Exception):
            TokenEncryptor("not-a-valid-fernet-key")

    def test_decrypt_invalid_ciphertext_raises(self):
        encryptor = TokenEncryptor(Fernet.generate_key().decode())

        with pytest.raises(InvalidToken):
            encryptor.decrypt("not-valid-ciphertext")
