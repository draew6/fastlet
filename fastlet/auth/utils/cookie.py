from fastapi import Response
from datetime import datetime, timedelta, UTC
from itsdangerous import Signer

from .token import JWTPayload
from ...deps.cookie import AuthCookies
from ...utils.settings import get_settings
from ..utils.token import verify_jwt as verify_jwt_token


def get_signer() -> Signer:
    settings = get_settings("bff")
    return Signer(settings.cookie_secret)


def set_cookie(response: Response, name: str, value: str):
    """
    Set a cookie in the response.
    """
    signer = get_signer()
    signed_value = signer.sign(value.encode()).decode()

    response.set_cookie(
        name,
        signed_value,
        expires=datetime.now(UTC) + timedelta(days=40),
        secure=True,
        samesite="none",
        httponly=True,
    )


async def verify_jwt(
    cookies: AuthCookies,
) -> JWTPayload:
    return await verify_jwt_token(cookies.access_token)
