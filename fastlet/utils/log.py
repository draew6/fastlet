from fastapi import BackgroundTasks

from .settings import get_settings
from ..queries.redis import get_activity_redis_client
import json
from pydantic import BaseModel
from datetime import datetime, UTC


class Activity(BaseModel):
    text: str
    user_id: int | None = None
    created_at: datetime

class ActivityLog:
    def __init__(self, bg: BackgroundTasks):
        self._client = get_activity_redis_client()
        self._settings = get_settings("bff")
        self._bg = bg

    async def get_recent_activity(self, limit: int = 30, user_id: int | None = None) -> list[Activity]:
        key = f"activity:{self._settings.project_name.lower()}" if user_id is None else f"activity:{self._settings.project_name.lower()}:{user_id}"
        logs = await self._client.lrange(key, -limit, -1)
        await self._client.close()
        return [Activity(**json.loads(log)) for log in logs]

    async def _write_to_redis(self, text: str, user_id: int | None = None) -> None:
        project = self._settings.project_name.lower()
        now = datetime.now(UTC)
        activity = Activity(text=text, user_id=user_id, created_at=now)

        root_key = f"activity:{project}"
        await self._client.rpush(root_key, activity.model_dump_json())
        await self._client.ltrim(root_key, 0, 500_000)  # keep last 500 000

        if user_id is not None:
            user_key = f"{root_key}:{user_id}"
            await self._client.rpush(user_key, activity.model_dump_json())
            await self._client.ltrim(user_key, 0, 5_000)  # keep last 5 000
        await self._client.close()

    def log(self, text: str, user_id: int | None = None) -> None:
        self._bg.add_task(self._write_to_redis, text, user_id)

    def __call__(self, text: str, user_id: int | None = None) -> None:
        self.log(text, user_id)

def get_activity_log(bg: BackgroundTasks) -> ActivityLog:
    return ActivityLog(bg)