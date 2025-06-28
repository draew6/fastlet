from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from importlib import import_module
import pkgutil
import re

from pydantic import ValidationError

from ..utils.settings import get_settings


def autoload(app: FastAPI | APIRouter, package_name: str):
    package = import_module(package_name)
    for loader, module_name, is_pkg in pkgutil.iter_modules(
        package.__path__, package_name + "."
    ):
        module = import_module(module_name)
        if hasattr(module, "router"):
            app.include_router(module.router)
        if is_pkg:
            autoload(app, module_name)

def allow_cors(app: FastAPI):
    try:
        settings = get_settings("bff")
    except ValidationError:
        settings = get_settings("auth")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8001"],
        allow_credentials=True,
        allow_origin_regex=rf"^https?://(?:[a-z0-9-]+\.)*{re.escape(settings.project_root_domain)}(?::\d+)?$",
        allow_methods=["*"],
        allow_headers=["*"],
    )