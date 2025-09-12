import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app import crud, models


# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


# Password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# User authentication
def authenticate_user(db: Session, username: str, password: str):
    user = crud.check_user(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# Token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    subject = str(data.get("sub"))
    to_encode.update({"exp": expire, "sub": subject})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_token_optional(request: Request) -> Optional[str]:
    """
    Wrapper to make sure we return None when no token is provided,
    instead of empty string "" from OAuth2PasswordBearer.
    """
    token: Optional[str] = await oauth2_scheme(request)
    if not token or token.strip() == "":
        return None
    return token


# Get current user from token
def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing username",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token decode failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = crud.check_user(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Return current user if token is valid,
    otherwise return None (anonymous user).
    """
    if not token:  # no token provided or empty string
        return None


    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if not username or not isinstance(username, str):
            return None

        

    except JWTError:
        return None

    return crud.check_user(db, username=username)

