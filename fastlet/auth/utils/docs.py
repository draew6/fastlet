from fastapi.security import OAuth2PasswordRequestForm
from fastlet.models.auth import UserAuth, LoginCredentials
from fastapi import Depends
from typing import Annotated
from ..authentication import authenticate_user
from ...deps.auth import AuthQueries


async def authenticate_user_for_docs(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: AuthQueries
) -> UserAuth | None:
    return await authenticate_user(
        LoginCredentials(username=credentials.username, password=credentials.password),
        db,
    )
