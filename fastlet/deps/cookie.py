from typing import Annotated
from ..models import AuthCookie
from fastapi import Depends
from ..auth.authentication import get_unsigned_auth_cookies

AuthCookies = Annotated[AuthCookie, Depends(get_unsigned_auth_cookies)]
