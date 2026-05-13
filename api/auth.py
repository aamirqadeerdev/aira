from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

# ── CONFIGURATION ──
SECRET_KEY      = os.getenv("SECRET_KEY", "aira-secret-key-change-in-production")
ALGORITHM       = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ── PASSWORD HASHING ──
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── OAUTH2 SCHEME ──
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── PASSWORD FUNCTIONS ──

def hash_password(password: str) -> str:
    """Convert plain password to secure hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if plain password matches stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ── TOKEN FUNCTIONS ──

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token for authenticated user."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ── CURRENT USER DEPENDENCY ──

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Extract and validate current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please sign in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    return {"email": email, "role": payload.get("role", "viewer")}

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Allow access only to admin users."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for this operation."
        )
    return current_user

async def require_analyst(current_user: dict = Depends(get_current_user)) -> dict:
    """Allow access to admin and analyst users."""
    if current_user.get("role") not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst access required for this operation."
        )
    return current_user
