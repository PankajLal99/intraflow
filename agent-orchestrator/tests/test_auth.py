"""
Tests for authentication module
"""

import pytest
from datetime import datetime, timedelta
from src.auth.password import hash_password, verify_password
from src.auth.jwt import create_access_token, verify_token
from jose import JWTError


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_verify_password_success(self):
        """Test password verification with correct password"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Test password verification with wrong password"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword", hashed) is False


class TestJWT:
    """Test JWT token functions"""
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {
            "user_id": "test-user-123",
            "tenant_id": "test-tenant-123",
            "email": "test@example.com",
            "role": "owner"
        }
        
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2
    
    def test_verify_token_success(self):
        """Test JWT token verification with valid token"""
        data = {
            "user_id": "test-user-123",
            "tenant_id": "test-tenant-123",
            "email": "test@example.com",
            "role": "owner"
        }
        
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert payload["user_id"] == data["user_id"]
        assert payload["tenant_id"] == data["tenant_id"]
        assert payload["email"] == data["email"]
        assert payload["role"] == data["role"]
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_token_expired(self):
        """Test JWT token verification with expired token"""
        data = {
            "user_id": "test-user-123",
            "tenant_id": "test-tenant-123"
        }
        
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expired_delta)
        
        with pytest.raises(Exception):
            verify_token(token)
    
    def test_verify_token_invalid(self):
        """Test JWT token verification with invalid token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            verify_token(invalid_token)
