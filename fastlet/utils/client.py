from ..auth.authentication import AuthCookies
from ..auth.utils.token import create_system_access_token


class Client:

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        for client in self._iter_clients():
            await client._client.aclose()  # Close each client


    def _iter_clients(self):
        for _name, attr in vars(self).items():
            if (
                    callable(getattr(attr, "set_access_token", None))
                    and getattr(attr, "_client", None) is not None
            ):
                yield attr

    @classmethod
    def get_client(cls, cookies: AuthCookies):
        client = cls()
        if cookies:
            for cl in client._iter_clients():
                cl.set_access_token(cookies.access_token)
        return client

    @classmethod
    def get_system_client(cls):
        client = cls()
        for cl in client._iter_clients():
            cl.set_access_token(create_system_access_token())
        return client
