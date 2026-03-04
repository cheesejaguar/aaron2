import pytest
from pydantic import ValidationError

from app.schemas.user import LoginRequest, UserCreate, UserRead


class TestUserCreate:
    def test_valid_user_create(self):
        u = UserCreate(email="test@test.com", name="Test", password="secret123")
        assert u.email == "test@test.com"
        assert u.name == "Test"
        assert u.password == "secret123"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", name="Test", password="secret")

    def test_missing_fields_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@test.com")  # type: ignore[call-arg]


class TestLoginRequest:
    def test_valid_login(self):
        lr = LoginRequest(email="test@test.com", password="secret")
        assert lr.email == "test@test.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="bad", password="secret")


class TestUserRead:
    def test_user_read_serialization(self):
        from uuid import uuid4

        uid = uuid4()
        ur = UserRead(id=uid, email="test@test.com", name="Test")
        assert ur.id == uid
        assert ur.health_goals_json is None
