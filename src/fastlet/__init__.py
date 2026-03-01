import importlib
import pkgutil
import re
from importlib import import_module
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if TYPE_CHECKING:
    from fastlet.auth import (
        Admin,
        AdminOrSelf,
        AuthTokens,
        MustBeSelf,
        OptionalUser,
        Settings,
        System,
        SystemOrSelf,
        User,
        UserInfo,
        VerifiedAuthTokens,
        authenticated_client,
        create_access_token,
        create_system_access_token,
        create_token,
        get_settings,
        set_cookie,
    )
    from fastlet.client import BaseClient, create_client, create_system_client, service
    from fastlet.db import close_pool, create_queries_dependency, get_pool, init_pool, setup


def allow_cors(app: FastAPI) -> None:
    from crotal.config import get_settings

    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8001"],
        allow_credentials=True,
        allow_origin_regex=rf"^https?://(?:[a-z0-9-]+\.)*{re.escape(settings.root_domain)}(?::\d+)?$",
        allow_methods=["*"],
        allow_headers=["*"],
    )


def autoload(app: FastAPI, package_name: str) -> None:
    package = import_module(package_name)
    for loader, module_name, is_pkg in pkgutil.iter_modules(
        package.__path__, package_name + "."
    ):
        module = import_module(module_name)
        if hasattr(module, "router"):
            app.include_router(module.router)
        if is_pkg:
            autoload(app, module_name)


_MODULES = {
    "auth": {
        "Admin", "AdminOrSelf", "AuthTokens", "MustBeSelf", "OptionalUser",
        "Settings", "System", "SystemOrSelf", "User", "UserInfo",
        "VerifiedAuthTokens", "authenticated_client", "create_access_token",
        "create_system_access_token", "create_token", "get_settings",
        "set_cookie",
    },
    "client": {
        "BaseClient", "service", "create_client", "create_system_client",
    },
    "db": {
        "close_pool", "create_queries_dependency", "get_pool", "init_pool", "setup",
    },
}

_LOOKUP = {name: mod for mod, names in _MODULES.items() for name in names}
__all__ = [*_LOOKUP, "allow_cors", "autoload"]


def __getattr__(name: str) -> object:
    if mod := _LOOKUP.get(name):
        return getattr(importlib.import_module(f"fastlet.{mod}"), name)
    raise AttributeError(f"module 'fastlet' has no attribute {name!r}")
