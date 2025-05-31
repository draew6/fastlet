from piping_bag.decorators import query


class TestQueries:
    @query("""SELECT token FROM reset WHERE user_id = $user_id""")
    async def get_reset_token(self, user_id: int) -> str | None: ...

    @query(
        """INSERT INTO user (username, password, role, displayname, mail) VALUES ("admin", $password, "ADMIN", "admin", "admin@admin.sk")"""
    )
    async def create_admin(self, password: str) -> None: ...
