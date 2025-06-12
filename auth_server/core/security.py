import os, uuid
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from pathlib import Path

ALGO = "RS256"
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

with open(Path(os.getenv("PRIVATE_KEY_PATH"))) as f:
    _PRIVATE = f.read()
with open(Path(os.getenv("PUBLIC_KEY_PATH"))) as f:
    PUBLIC_KEY = f.read()

def hash_pw(pw):
    return pwd_ctx.hash(pw)

def verify_pw(pw, h):
    return pwd_ctx.verify(pw, h)

def _token(sub: str, minutes: int, scope: str) -> str:
    now = datetime.now(tz=timezone.utc)
    return jwt.encode({
        "iss": os.getenv("ISSUER"),
        "sub": sub,
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
        "scope": scope,
        "jti": str(uuid.uuid4())
    }, _PRIVATE, algorithm=ALGO)

def new_access(uid: int):
    return _token(str(uid), int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")), "access")

def new_refresh(uid: int):
    return _token(str(uid), int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")) * 1440, "refresh")

def decode(tok: str):
    return jwt.decode(tok, PUBLIC_KEY, algorithms=[ALGO], issuer=os.getenv("ISSUER"))
