from fastapi import Depends, HTTPException
from typing import Annotated, TypeVar, Type
from .utils.token import verify_jwt, JWTPayload
from ..models.auth import UserAuth
from .authentication import get_user_by_id
from ..models.payloads import UserIDsPayload
from ..deps.auth import AuthQueries


class User(JWTPayload):
    requested_user_id: int


async def authorize(
    payload: Annotated[JWTPayload | None, Depends(verify_jwt)], db: AuthQueries
) -> UserAuth:
    user_id = payload.id
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=401)
    return user


async def authorize_admin(user: Annotated[UserAuth, Depends(authorize)]) -> UserAuth:
    if user and user.role == "ADMIN":
        return user
    raise HTTPException(status_code=401)


async def authorize_admin_or_self(
    user: Annotated[JWTPayload, Depends(authorize)], user_id: int
) -> User:
    if user_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403)
    return User(**user.model_dump(), requested_user_id=user_id)


async def authorize_system(
    user: Annotated[JWTPayload, Depends(authorize)],
) -> JWTPayload:
    if user.role == "ADMIN" or user.role == "SYSTEM":
        return user
    raise HTTPException(status_code=401)


T = TypeVar("T", bound=UserIDsPayload)


def only_self_allowed(model_cls: Type[T]):
    async def only_self_allowed_check(
        user: Annotated[JWTPayload, Depends(authorize)], body: model_cls
    ) -> model_cls:
        if len(body.user_ids) > 1 and user.role != "ADMIN":
            raise HTTPException(status_code=403)
        if user.role != "ADMIN" and [user.id] != body.user_ids:
            raise HTTPException(status_code=403)
        return body

    return only_self_allowed_check
