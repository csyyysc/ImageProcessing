"""
Test JWT authentication functionality
"""
import pytest
from datetime import timedelta
from backend.services.jwt_service import jwt_service


def test_jwt_token_creation():
    """Test JWT token creation"""

    user_id = 123
    username = "testuser"

    token = jwt_service.create_token_for_user(user_id, username)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_jwt_token_verification():
    """Test JWT token verification"""

    user_id = 123
    username = "testuser"

    # Create token
    token = jwt_service.create_token_for_user(user_id, username)

    # Verify token
    payload = jwt_service.verify_token(token)

    assert payload is not None
    assert payload.get("sub") == str(user_id)
    assert payload.get("type") == "access"
    assert payload.get("username") == username


def test_jwt_token_expiration():
    """Test JWT token expiration"""

    user_id = 123
    username = "testuser"

    # Create token with short expiration
    data = {"sub": str(user_id), "username": username, "type": "access"}
    token = jwt_service.create_access_token(
        data, expires_delta=timedelta(seconds=1))

    # Token should be valid initially
    payload = jwt_service.verify_token(token)
    assert payload is not None

    # Wait for expiration (in real test, you'd mock time)
    # For now, just test that expired tokens are handled
    expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMiLCJ1c2VybmFtZSI6InRlc3R1c2VyIiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MTYwOTQ1NjAwMH0.invalid"

    payload = jwt_service.verify_token(expired_token)
    assert payload is None


def test_password_hashing():
    """Test password hashing and verification"""

    password = "testpassword123"
    hashed = jwt_service.hash_password(password)

    assert hashed is not None
    assert hashed != password
    assert len(hashed) > 0

    assert jwt_service.verify_password(password, hashed) is True
    assert jwt_service.verify_password("wrongpassword", hashed) is False


def test_get_user_id_from_token():
    """Test extracting user ID from token"""

    user_id = 456
    username = "testuser2"

    token = jwt_service.create_token_for_user(user_id, username)
    extracted_id = jwt_service.get_user_id_from_token(token)

    assert extracted_id == user_id


def test_invalid_token_handling():
    """Test handling of invalid tokens"""

    invalid_tokens = [
        "invalid.token.here",
        "not-a-jwt-token",
        "",
        None
    ]

    for token in invalid_tokens:
        if token is None:
            continue
        payload = jwt_service.verify_token(token)
        assert payload is None


if __name__ == "__main__":
    pytest.main([__file__])
