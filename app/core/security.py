from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(data: dict, expire_delta: timedelta) -> str:
    payload = data.copy()
    now = datetime.now(timezone.utc)
    payload["iat"] = now
    payload["exp"] = now + expire_delta
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.refresh_token_expire_days),
    )


def create_reset_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "password_reset"},
        timedelta(minutes=settings.reset_token_expire_minutes),
    )


def decode_token(token: str, expected_type: str) -> int:
    """Decode a JWT and return the user_id. Raises JWTError on any failure."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    if payload.get("type") != expected_type:
        raise JWTError("Invalid token type")
    sub = payload.get("sub")
    if sub is None:
        raise JWTError("Missing subject")
    return int(sub)


def token_issued_at(token: str) -> datetime | None:
    """Return the iat claim of a token without validating expiry."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"verify_exp": False},
        )
        iat = payload.get("iat")
        if iat is None:
            return None
        return datetime.fromtimestamp(iat, tz=timezone.utc)
    except JWTError:
        return None
