from typing import Annotated
from ..queries.auth import get_db, AuthQueries
from fastapi import Depends


AuthQueries = Annotated[AuthQueries, Depends(get_db)]
