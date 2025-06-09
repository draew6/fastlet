from typing import Annotated

from ..auth.utils.token import JWTPayload
from ..queries.auth import get_db, AuthQueries
from fastapi import Depends
from ..models.auth import AuthCookie
from fastapi import Cookie
from ..auth.utils.cookie import verify_jwt


AuthQueries = Annotated[AuthQueries, Depends(get_db)]
RawAuthCookies = Annotated[AuthCookie, Cookie()]
User = Annotated[JWTPayload, Depends(verify_jwt)]
