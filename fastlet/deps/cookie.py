from typing import Annotated
from ..models import AuthCookie
from fastapi import Depends
from ..auth.authentication import get_unsigned_auth_cookies
from ..auth.utils.cookie import verify_jwt as verify_jwt_cookie
from ..auth.utils.token import JWTPayload


User = Annotated[JWTPayload, Depends(verify_jwt_cookie)]
AuthCookies = Annotated[AuthCookie, Depends(get_unsigned_auth_cookies)]
