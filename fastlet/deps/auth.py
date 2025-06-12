from typing import Annotated
from ..queries.auth import get_db, AuthQueries
from fastapi import Depends, Request, HTTPException
from ..models.auth import AuthCookie
from pydantic import BaseModel, ValidationError


def NewCookie[T: BaseModel](model: type[T]):
    def dependency(request: Request) -> T:
        try:
            data = {field: request.cookies.get(field) for field in model.model_fields}
            return model(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.errors())
    return dependency



AuthQueries = Annotated[AuthQueries, Depends(get_db)]
RawAuthCookies = Annotated[AuthCookie, Depends(NewCookie(AuthCookie))]
