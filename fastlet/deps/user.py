from ..auth.authentication import verify_jwt_cookie
from ..auth.utils.token import JWTPayload
from typing import Annotated
from fastapi import Depends

User = Annotated[JWTPayload, Depends(verify_jwt_cookie)]