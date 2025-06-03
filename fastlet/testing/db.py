import os
from typing import Type

from fastapi import FastAPI
from piping_bag.interfaces import SQLiteDatabase
from piping_bag.queries import BaseQueries
from ..utils.db import create_sqlite_schema, run_scripts, push_to_db
from pytest import fixture
from ..testing.queries import TestQueries
from ..queries.auth import get_db
from ..utils.mail import get_mail_sender, get_mail_sender_mock


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

def prepare_test_environment(app: FastAPI, queries: Type[BaseQueries], get_db_fn: callable):
    class TestQ(queries, TestQueries): ...

    def get_test_db() -> TestQueries:
        return TestQ(SQLiteDatabase("db/internals/test.db"))

    os.environ["ENV"] = "TEST"
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_db_fn] = get_test_db
    app.dependency_overrides[get_mail_sender] = get_mail_sender_mock

    return get_test_db

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
