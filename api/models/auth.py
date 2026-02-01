# api/models/auth.py
"""
Authentication Pydantic models
"""
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    user_id: str
    email: str
    token: str
    expires_in: int  # seconds


class HeartbeatRequest(BaseModel):
    """Session heartbeat"""
    session_id: str


class HeartbeatResponse(BaseModel):
    """Heartbeat response"""
    alive: bool
    expires_in: int  # seconds
