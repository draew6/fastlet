from typing import Annotated
from ..queries.auth import get_db, AuthQueries
from fastapi import Depends, Request, HTTPException
from ..models.auth import AuthCookie
from pydantic import BaseModel, ValidationError


def NewCookie[T: BaseModel](model: type[T]):
    def dependency(request: Request) -> T | None:
        try:
            data = {field: request.cookies.get(field) for field in model.model_fields}
            return model(**data)
        except ValidationError as e:
            print(e.errors())
            return None
    return dependency



AuthQueries = Annotated[AuthQueries, Depends(get_db)]
RawAuthCookies = Annotated[AuthCookie | None, Depends(NewCookie(AuthCookie))]
