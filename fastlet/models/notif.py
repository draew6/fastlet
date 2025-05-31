from ..models.auth import DeviceInfo
from pydantic import BaseModel


class MassNotificationBody(BaseModel):
    devices: list[DeviceInfo]
    message: str


class MassNotificationResponse(BaseModel):
    success: list[DeviceInfo]
    failed: list[DeviceInfo]
