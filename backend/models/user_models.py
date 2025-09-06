"""
User models with validation
"""
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Enhanced user creation model"""
    username: str = Field(..., min_length=3, max_length=50,
                          description="Username (3-50 characters)")
    email: Optional[EmailStr] = Field(None, description="Valid email address")
    password: str = Field(..., min_length=8,
                          description="Password (minimum 8 characters)")

    @field_validator('username')
    def validate_username(cls, v):
        """Validate username format"""

        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError(
                'Username can only contain letters, numbers, and underscores')
        return v.lower()

    @field_validator('password')
    def validate_password(cls, v):
        """Validate password strength"""

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v


class UserLogin(BaseModel):
    """User login model"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    class Config:
        extra = "forbid"  # Prevent unexpected fields


class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool
    message: str
    user: Optional[UserResponse] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"
