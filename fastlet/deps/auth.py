from typing import Annotated
from ..auth.utils.cookie import get_signed_auth_cookies
from ..queries.auth import get_db, AuthQueries
from fastapi import Depends
from ..models.auth import AuthCookie
from fastapi import Cookie


AuthQueries = Annotated[AuthQueries, Depends(get_db)]
RawAuthCookies = Annotated[AuthCookie, Cookie()]
AuthCookies = Annotated[AuthCookie, Depends(get_signed_auth_cookies)]
