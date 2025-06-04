from ..models.auth import UserAuth, DeviceInfo, Mail, LoginCredentials, RefreshTokenBody
from fastapi import HTTPException
from .utils.password import verify_password
from ..deps.auth import AuthQueries, RawAuthCookies
from ..auth.utils.cookie import get_signer
from ..models.auth import AuthCookie


async def get_user_by_id(user_id: int, db: AuthQueries) -> UserAuth | None:
    return await db.get_user_by_id(user_id)


async def get_user_by_device(
    device_info: DeviceInfo, db: AuthQueries
) -> UserAuth | None:
    if "apple" in device_info.endpoint:
        return await db.get_user_by_device(
            device_info.auth, device_info.p256dh, device_info.endpoint
        )
    raise HTTPException(status_code=400, detail="Only apple devices are supported")


async def get_user_by_refresh_token(
    body: RefreshTokenBody, db: AuthQueries
) -> UserAuth | None:
    return await db.get_user_by_refresh_token(body.refresh_token)


async def get_user_by_mail(body: Mail, db: AuthQueries) -> UserAuth | None:
    return await db.get_user_by_mail(body.mail.lower())


async def authenticate_user(
    credentials: LoginCredentials, db: AuthQueries
) -> UserAuth | None:
    user = await db.get_user_by_name(credentials.username.lower())
    if user and verify_password(credentials.password, user.password):
        return user
    else:
        return None


def get_signed_auth_cookies(cookies: RawAuthCookies) -> AuthCookie:
    signer = get_signer()
    unsigned_refresh_token = signer.unsign(cookies.refresh_token)
    unsigned_access_token = signer.unsign(cookies.access_token)
    return AuthCookie(
        access_token=unsigned_access_token.decode(),
        refresh_token=unsigned_refresh_token.decode(),
    )
