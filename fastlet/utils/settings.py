from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal, overload
import os
from logging import getLogger


class ServiceWithoutDBSettings(BaseSettings):
    app_secret: str
    app_url: str = "localhost"
    project_name: str = "Project"
    auth_service: str = "localhost:8000/login"
    env: Literal["TEST", "DEV", "STAG", "PROD"] = "TEST"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @classmethod
    def test(cls):
        return cls(
            app_secret="test_secret",
            app_url="http://localhost:8000",
        )


# TODO: PORT as int?
# TODO: SCHEMA removed or optional?
class ServiceWithDBSettings(ServiceWithoutDBSettings):
    db_user: str = "postgres"
    db_password: str
    db_host: str
    db_port: str = "5432"
    db_name: str = "postgres"
    db_schema: str
    db_prisma_url: str = 'prismaurl'

    @classmethod
    def test(cls):
        return cls(
            **ServiceWithoutDBSettings.test().model_dump(),
            db_host="localhost",
            db_password="test_password",
            db_schema="public"
        )


class AuthSettings(ServiceWithDBSettings):
    sendgrid_api_key: str
    sendgrid_from_mail: str
    pwa_enabled: bool = False
    registration_enabled: bool = False
    project_root_domain: str

    @classmethod
    def test(cls):
        return cls(
            **ServiceWithDBSettings.test().model_dump(),
            sendgrid_api_key="test_sendgrid_api_key",
            sendgrid_from_mail="test@test.test",
            project_root_domain = "localhost",
            registration_enabled=True,
            pwa_enabled=True
        )


class NotifSettings(ServiceWithoutDBSettings):
    vapid_key: str
    vapid_mailto: str

    @classmethod
    def test(cls):
        return cls(
            **ServiceWithoutDBSettings.test().model_dump(),
            vapid_key="test_vapid_key",
            vapid_mailto="test_valid@mail.to"
        )

class BFFServiceSettings(ServiceWithoutDBSettings):
    cookie_secret: str
    project_root_domain: str
    activity_redis_host: str | None = None
    activity_redis_port: str | None = None
    activity_redis_username: str | None = None
    activity_redis_password: str | None = None

    @classmethod
    def test(cls):
        return cls(
            **ServiceWithoutDBSettings.test().model_dump(),
            cookie_secret="test_cookie_secret",
            project_root_domain = "localhost",
        )


@overload
def get_settings(service_type: Literal["auth"]) -> AuthSettings: ...
@overload
def get_settings(service_type: Literal["notif"]) -> NotifSettings: ...
@overload
def get_settings(
    service_type: Literal["service_without_db"],
) -> ServiceWithoutDBSettings: ...
@overload
def get_settings(service_type: Literal["service_with_db"]) -> ServiceWithDBSettings: ...
@overload
def get_settings(service_type: Literal["bff"]) -> BFFServiceSettings: ...


@lru_cache
def get_settings(
    service_type: Literal[
        "auth", "notif", "service_without_db", "service_with_db", "bff"
    ],
) -> (
        ServiceWithoutDBSettings
        | ServiceWithDBSettings
        | AuthSettings
        | NotifSettings
        | BFFServiceSettings
):
    if service_type == "auth":
        settings = AuthSettings
    elif service_type == "notif":
        settings = NotifSettings
    elif service_type == "service_without_db":
        settings = ServiceWithoutDBSettings
    elif service_type == "service_with_db":
        settings = ServiceWithDBSettings
    elif service_type == "bff":
        settings = BFFServiceSettings
    else:
        raise ValueError(f"Unknown service type: {service_type}")
    if os.environ.get("ENV") == "TEST":
        settings.model_config["env_file"] = None
        return settings.test()
    return settings()
