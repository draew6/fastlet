from pydantic import BaseModel, Field


class UserIDsPayload(BaseModel):
    user_ids: list[int] = Field(..., title="List of User IDs", min_length=1)
