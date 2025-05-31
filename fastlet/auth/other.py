from .utils.token import create_token
from datetime import datetime, UTC
from ..deps.auth import AuthQueries


async def create_refresh_token(user_id: int, db: AuthQueries) -> str:
    refresh_token = create_token()
    date_created = datetime.now(UTC)
    return await db.create_refresh_token(refresh_token, user_id, date_created)
