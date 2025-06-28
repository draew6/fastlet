from fastlet.auth.authentication import AuthCookies

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

    @staticmethod
    def get_client(cookies: AuthCookies):
        client = Client()
        for cl in client._iter_clients():
            cl.set_access_token(cookies.access_token)
        return client
