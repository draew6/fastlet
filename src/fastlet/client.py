from __future__ import annotations

import sys
from collections.abc import AsyncIterator
from typing import Annotated, get_type_hints

import httpx
from fastapi import Depends, HTTPException, Request


def service[T](client_cls: type[T], base_url: str, *, timeout: float | None = 30.0) -> T:
    """Create a generated API client instance.

    Usage::

        self.posting = service(PostingClient, "https://posting.api")
        self.match = service(MatchClient, "https://match.api", timeout=10)
    """
    module = sys.modules[client_cls.__module__]
    config_cls = getattr(module, "ClientConfig")
    return client_cls(config_cls(base_url=base_url, timeout=timeout))  # type: ignore[call-arg]


def _set_token(client: httpx.AsyncClient, token: str | None) -> None:
    if token:
        client.headers["Authorization"] = f"Bearer {token}"
    else:
        client.headers.pop("Authorization", None)


class BaseClient:
    """Base unified client with per-service auth.

    Subclass and define services in ``__init__``::

        class APIClient(BaseClient):
            def __init__(self):
                self.posting = service(PostingClient, "https://posting.api")
                self.match = service(MatchClient, "https://match.api", timeout=10)
                self.user = service(UserClient, "https://user.api")
    """

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        original_init = cls.__init__

        def wrapped_init(self: BaseClient, *args: object, **kw: object) -> None:
            original_init(self, *args, **kw)  # type: ignore[misc]
            self._discover_services()

        cls.__init__ = wrapped_init  # type: ignore[method-assign]

    def _discover_services(self) -> None:
        self._http_clients: dict[str, httpx.AsyncClient] = {}
        for name, value in vars(self).items():
            if name.startswith("_"):
                continue
            transport = getattr(value, "transport", None)
            if transport is None:
                continue
            http_client = getattr(transport, "_client", None)
            if isinstance(http_client, httpx.AsyncClient):
                self._http_clients[name] = http_client

    def set_access_token(self, access_token: str | None) -> None:
        """Set token for ALL services."""
        for client in self._http_clients.values():
            _set_token(client, access_token)

    def set_service_token(self, service_name: str, access_token: str | None) -> None:
        """Set token for a specific service."""
        _set_token(self._http_clients[service_name], access_token)

    async def close(self) -> None:
        for name in self._http_clients:
            await getattr(self, name).close()

    async def __aenter__(self) -> BaseClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()


def create_client[T: BaseClient](client_cls: type[T]) -> type[T]:
    """Create a FastAPI dependency that forwards the user's Bearer token.

    Usage::

        class MyClient(BaseClient):
            def __init__(self):
                self.users = service(UsersClient, "https://users.api")

        Client = create_client(MyClient)
        SystemClient = create_system_client(MyClient)

        @router.get("/users")
        async def list_users(client: Client):
            return await client.users.list_users()
    """

    async def _dependency(request: Request) -> AsyncIterator[T]:
        client = client_cls()
        auth = request.headers.get("authorization", "")
        token = auth.removeprefix("Bearer ").strip() if auth else None
        if token:
            client.set_access_token(token)
        try:
            yield client
        except Exception as exc:
            if status := getattr(exc, "status_code", None):
                raise HTTPException(status_code=status, detail=str(exc)) from exc
            raise
        finally:
            await client.close()

    return Annotated[T, Depends(_dependency)]  # type: ignore[return-value]


def create_system_client[T: BaseClient](client_cls: type[T]) -> type[T]:
    """Create a FastAPI dependency that uses a system access token.

    Usage::

        SystemClient = create_system_client(MyClient)

        @router.get("/sync")
        async def sync_data(client: SystemClient):
            return await client.users.list_users()
    """

    async def _dependency() -> AsyncIterator[T]:
        from crotal.tokens import create_system_access_token

        client = client_cls()
        client.set_access_token(create_system_access_token())
        try:
            yield client
        except Exception as exc:
            if status := getattr(exc, "status_code", None):
                raise HTTPException(status_code=status, detail=str(exc)) from exc
            raise
        finally:
            await client.close()

    return Annotated[T, Depends(_dependency)]  # type: ignore[return-value]
