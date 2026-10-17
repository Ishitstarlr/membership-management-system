import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import bcrypt
if not hasattr(bcrypt, "__about__"):
    class _BcryptAbout:
        __version__ = getattr(bcrypt, "__version__", "4.2.1")
    bcrypt.__about__ = _BcryptAbout()

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import RoleEnum

SECRET_KEY = os.getenv("JWT_SECRET", "acm-nitk-membership-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required for this action",
        )
    return current_user
