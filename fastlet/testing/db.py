import os
from ..utils.db import create_sqlite_schema, run_scripts, push_to_db
from pytest import fixture


@fixture(scope="function", autouse=True)
def build_db():
    delete_db()
    create_sqlite_schema("db/internals/schema.sqlite3.prisma", "./test.db")
    push_to_db("test")
    run_scripts("db/internals/test.db")
    # enable_foreign_keys()
    yield


def delete_db():
    if os.path.exists("db/internals/test.db"):
        os.remove("db/internals/test.db")


"""
def enable_foreign_keys():
    conn = sqlite3.connect("db/test.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys")
    print(cursor.fetchall())
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA foreign_keys")
    print(cursor.fetchall())
    conn.commit()
    conn.close()
"""
