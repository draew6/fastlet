from piping_bag.interfaces import PostgresDatabase, SQLiteDatabase
from piping_bag.decorators import query
from piping_bag.queries import BaseQueries

from ..utils.settings import get_settings
from ..models.auth import UserAuth
from datetime import datetime


class AuthQueries(BaseQueries):
    @query("""SELECT * FROM userauth WHERE username = $username""")
    async def get_user_by_name(self, username: str) -> UserAuth | None: ...

    @query("""SELECT * FROM userauth WHERE id = $user_id""")
    async def get_user_by_id(self, user_id: int) -> UserAuth | None: ...

    @query("""SELECT * FROM userauth WHERE refresh_token = $refresh_token""")
    async def get_user_by_refresh_token(
        self, refresh_token: str
    ) -> UserAuth | None: ...

    @query("""SELECT * FROM userauth
        LEFT JOIN device d on userauth.id = d.user_id
        WHERE d.auth = $auth AND d.p256dh = $p256dh AND d.endpoint = $endpoint""")
    async def get_user_by_device(
        self, auth: str, p256dh: str, endpoint: str
    ) -> UserAuth | None: ...

    @query("""SELECT * FROM userauth WHERE mail = $mail""")
    async def get_user_by_mail(self, mail: str) -> UserAuth | None: ...

    @query("""
        INSERT INTO refresh (token, user_id, date_created)
        VALUES ($token, $user_id, $date_created) RETURNING token """)
    async def create_refresh_token(
        self, token: str, user_id: int, date_created: datetime
    ) -> str: ...


def get_db() -> AuthQueries:
    settings = get_settings("service_with_db")
    if settings.env == "DEV":
        return AuthQueries(SQLiteDatabase("db/dev.db"))
    return AuthQueries(
        PostgresDatabase(
            db_name=settings.db_name,
            db_host=settings.db_host,
            db_port=settings.db_port,
            db_user=settings.db_user,
            db_password=settings.db_password,
        ),
        settings.db_schema,
    )
