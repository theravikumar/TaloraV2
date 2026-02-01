# api/routes/auth.py
"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.auth import UserRegister, UserLogin, TokenResponse, HeartbeatRequest, HeartbeatResponse
from api.services.auth_service import register_user, authenticate_user, create_user_token
from api.database.redis_client import RedisCache
from api.utils.errors import AuthenticationError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        user = register_user(db, user_data.email, user_data.password)
        return create_user_token(user)
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login existing user"""
    try:
        user = authenticate_user(db, credentials.email, credentials.password)
        return create_user_token(user)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/heartbeat", response_model=HeartbeatResponse)
def heartbeat(data: HeartbeatRequest):
    """Keep guest session alive"""
    success = RedisCache.update_heartbeat(data.session_id, ttl=300)
    return HeartbeatResponse(alive=success, expires_in=300 if success else 0)
