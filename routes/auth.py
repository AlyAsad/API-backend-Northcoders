import os
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import  HTTPException, Depends
from datetime import datetime, timedelta, timezone
import jwt

JWT_SECRET = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30) # expires after 30 mins
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        return int(jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM]
        )["sub"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
