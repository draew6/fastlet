from typing import Annotated


from ..queries.auth import get_db, AuthQueries
from fastapi import Depends
from ..models.auth import AuthCookie
from fastapi import Cookie


AuthQueries = Annotated[AuthQueries, Depends(get_db)]
RawAuthCookies = Annotated[AuthCookie, Cookie()]

