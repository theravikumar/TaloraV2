# api/services/auth_service.py
"""
Authentication service
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from api.database.models import User
from api.utils.errors import AuthenticationError, ERROR_MESSAGES
from api.utils.jwt import create_access_token

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def register_user(db: Session, email: str, password: str) -> User:
    """
    Register new user.
    
    Raises AuthenticationError if email already exists.
    """
    # Check if email exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise AuthenticationError(ERROR_MESSAGES["duplicate_email"])
    
    # Create user
    user = User(
        email=email,
        password_hash=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate user with email and password.
    
    Raises AuthenticationError if credentials invalid.
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError(ERROR_MESSAGES["invalid_credentials"])
    
    if not user.is_active:
        raise AuthenticationError("Account is disabled")
    
    return user


def create_user_token(user: User) -> dict:
    """Create JWT token for user"""
    token = create_access_token({"sub": user.id, "email": user.email})
    return {
        "user_id": user.id,
        "email": user.email,
        "token": token,
        "expires_in": 86400  # 24 hours
    }
