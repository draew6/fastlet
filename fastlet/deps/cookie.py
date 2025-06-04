from typing import Annotated
from ..models import AuthCookie
from fastapi import Depends
from ..auth.authentication import get_signed_auth_cookies

AuthCookies =Annotated[AuthCookie, Depends(get_signed_auth_cookies)]