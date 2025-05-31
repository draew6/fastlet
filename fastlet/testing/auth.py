from jose import jwt
from ..utils.settings import get_settings
from fastapi.testclient import TestClient
from typing import Literal


def get_token(
    client: TestClient,
    user_id: int,
    role: Literal["USER", "ADMIN", "TESTER", "SYSTEM"] = "USER",
):
    settings = get_settings("service_without_db")
    token = jwt.encode(
        {"id": user_id, "name": "admin", "role": role},
        settings.app_secret,
        algorithm="HS256",
    )
    client.headers = {"Authorization": f"Bearer {token}"}
