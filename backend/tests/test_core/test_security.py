from uuid import uuid4

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_returns_bcrypt_hash(self):
        hashed = hash_password("mysecret")
        assert hashed.startswith("$2b$")
        assert hashed != "mysecret"

    def test_hash_password_produces_unique_hashes(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # different salts

    def test_verify_password_correct(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_verify_password_empty_string(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False


class TestTokenCreation:
    def test_create_access_token_valid_jwt(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_refresh_token_valid_jwt(self):
        user_id = uuid4()
        token = create_refresh_token(user_id)
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_access_and_refresh_tokens_differ(self):
        user_id = uuid4()
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)
        assert access != refresh


class TestTokenDecoding:
    def test_decode_valid_token(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_decode_invalid_token_raises(self):
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token("not.a.valid.token")

    def test_decode_wrong_secret_raises(self):
        user_id = uuid4()
        token = jwt.encode(
            {"sub": str(user_id), "type": "access"},
            "wrong-secret",
            algorithm=ALGORITHM,
        )
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token(token)

    def test_decode_expired_token_raises(self):
        from datetime import UTC, datetime, timedelta

        user_id = uuid4()
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.now(UTC) - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token(token)
