from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal, overload
import os


class ServiceWithoutDBSettings(BaseSettings):
    app_secret: str
    app_url: str = "localhost"
    project_name: str = "Project"
    auth_service: str = "localhost:8000/login"
    env: Literal["TEST", "DEV", "STAG", "PROD"] = "TEST"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# TODO: PORT as int?
# TODO: SCHEMA removed or optional?
class ServiceWithDBSettings(ServiceWithoutDBSettings):
    db_user: str = "postgres"
    db_password: str
    db_host: str
    db_port: str = "5432"
    db_name: str = "postgres"
    db_schema: str


class AuthSettings(ServiceWithDBSettings):
    sendgrid_api_key: str
    sendgrid_from_mail: str
    pwa_enabled: bool = False
    registration_enabled: bool = False
    project_root_domain: str


class NotifSettings(ServiceWithDBSettings):
    vapid_key: str
    vapid_mailto: str


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


@lru_cache
def get_settings(
    service_type: Literal["auth", "notif", "service_without_db", "service_with_db"],
) -> ServiceWithoutDBSettings | ServiceWithDBSettings | AuthSettings | NotifSettings:
    if service_type == "auth":
        settings = AuthSettings
    elif service_type == "notif":
        settings = NotifSettings
    elif service_type == "service_without_db":
        settings = ServiceWithoutDBSettings
    elif service_type == "service_with_db":
        settings = ServiceWithDBSettings
    else:
        raise ValueError(f"Unknown service type: {service_type}")
    if os.environ.get("ENV") == "TEST":

        class TestSettings(settings):
            model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")

        return TestSettings()
    return settings()
