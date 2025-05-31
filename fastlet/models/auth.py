from typing import Literal
from pydantic import BaseModel, EmailStr, field_validator
from email_validator import validate_email, EmailNotValidError

role = Literal["USER", "ADMIN", "TESTER", "SYSTEM"]


class DeviceInfo(BaseModel):
    endpoint: str
    p256dh: str
    auth: str

    @property
    def subscription_info(self):
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }


class Device(DeviceInfo):
    id: int
    user_id: int


class User(BaseModel):
    id: int
    displayname: str


class UserAuth(User):
    role: role
    refresh_token: str | None
    password: str
    mail: str


class Mail(BaseModel):
    mail: EmailStr

    @field_validator("mail")
    @classmethod
    def validate_mail(cls, v):
        try:
            validate_email(v, check_deliverability=True)
        except EmailNotValidError:
            raise ValueError("Invalid mail")
        return v


class LoginCredentials(BaseModel):
    username: str
    password: str


class RefreshTokenBody(BaseModel):
    refresh_token: str
