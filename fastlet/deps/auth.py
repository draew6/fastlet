from typing import Annotated
from ..auth.authentication import get_signed_auth_cookies
from ..queries.auth import get_db, AuthQueries
from fastapi import Depends
from ..models.auth import AuthCookie


AuthQueries = Annotated[AuthQueries, Depends(get_db)]
AuthCookies = Annotated[AuthCookie, Depends(get_signed_auth_cookies)]
