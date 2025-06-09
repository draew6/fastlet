from datetime import datetime, UTC
from fastlet.utils.settings import get_settings
from jose import jwt
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
import secrets
from datetime import timedelta


class JWTPayload(BaseModel):
    id: int
    name: str
    role: str
    exp: datetime | None = None


settings = get_settings("service_without_db")

access_token_scheme = OAuth2PasswordBearer(tokenUrl=settings.auth_service)


def create_token() -> str:
    return secrets.token_hex(20)


def create_access_token(user_id: int, role: str, name: str) -> str:
    return jwt.encode(
        {"id": user_id, "role": role, "name": name}
        | {"exp": datetime.now(UTC) + timedelta(minutes=15)},
        settings.app_secret,
        algorithm="HS256",
    )
