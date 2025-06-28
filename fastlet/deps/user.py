from typing import Annotated
from fastapi import Depends
from ..auth.utils.token import JWTPayload
from ..auth.authorization import authorize, authorize_admin, authorize_system

User = Annotated[JWTPayload, Depends(authorize)]
Admin = Annotated[JWTPayload, Depends(authorize_admin)]
System = Annotated[JWTPayload, Depends(authorize_system)]