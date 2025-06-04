from fastapi import Response
from datetime import datetime, timedelta, UTC
from itsdangerous import Signer

from ...utils.settings import get_settings
from ...deps.auth import RawAuthCookies
from ...models.auth import AuthCookie

def get_signer() -> Signer:
    """
    """
    settings = get_settings("service_without_db")
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

def get_signed_auth_cookies(cookies: RawAuthCookies) -> AuthCookie:
    signer = get_signer()
    unsigned_refresh_token = signer.unsign(cookies.refresh_token)
    unsigned_access_token = signer.unsign(cookies.access_token)
    return AuthCookie(
        access_token=unsigned_access_token.decode(),
        refresh_token=unsigned_refresh_token.decode()
    )