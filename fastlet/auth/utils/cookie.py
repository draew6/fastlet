from fastapi import Response
from datetime import datetime, timedelta, UTC
from itsdangerous import Signer
from ...utils.settings import get_settings


def get_signer() -> Signer:
    settings = get_settings("bff")
    return Signer(settings.cookie_secret)


def set_cookie(response: Response, name: str, value: str):
    """
    Set a cookie in the response.
    """
    signer = get_signer()
    signed_value = signer.sign(value.encode()).decode()
    settings = get_settings("bff")

    response.set_cookie(
        name,
        signed_value,
        max_age=60*60*24*40,
        expires=60*60*24*40,
        # expires=datetime.now(UTC) + timedelta(days=40),
        secure=True,
        samesite="none",
        httponly=True,
        domain=settings.project_root_domain
    )
