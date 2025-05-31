from fastapi import FastAPI
from importlib import import_module
import pkgutil


def autoload(app: FastAPI, package_name: str):
    package = import_module(package_name)
    for loader, module_name, is_pkg in pkgutil.iter_modules(
        package.__path__, package_name + "."
    ):
        module = import_module(module_name)
        if hasattr(module, "router"):
            app.include_router(module.router)
