import re
import os
import sqlite3
import subprocess
from typing import Literal
from dotenv import load_dotenv


def create_sqlite_schema(
    output_file_path: str, db_path: str, prisma_file_path="db/schema.prisma"
):
    try:
        with open(prisma_file_path, "r") as file:
            content = file.read()
            lines = content.split("\n")
    except FileNotFoundError:
        print("File not found")
        print(os.listdir("db"))
        raise FileNotFoundError()
    enum_names = []
    for line in lines:
        if line.strip().startswith("enum "):
            enum_name = line.strip().split()[1]
            enum_names.append(enum_name)

    for enum_name in enum_names:
        content = content.replace(enum_name, "String")

    # Removing enum definitions
    content = re.sub(r"enum\s+\w+\s*\{[^}]*\}", "", content)

    # Ensuring string defaults are correctly quoted
    content = re.sub(r'(String\s+@default\()([^\s\'"]+)(\))', r'\1"\2"\3', content)

    content = content.replace("postgresql", "sqlite")
    content = content.replace('env("DB_PRISMA_URL")', f'"file:{db_path}"')
    content = content.replace("@db.Timestamptz(6)", "")

    os.makedirs("db/internals", exist_ok=True)
    with open(output_file_path, "w") as output_file:
        output_file.write(content)
        print("SQLite Schema Ready")


def push_to_db(environment: Literal["test", "dev", "stag"]):
    if environment == "stag":
        new_schema_file = "db/schema.prisma"
    else:
        new_schema_file = "db/internals/schema.sqlite3.prisma"
        create_sqlite_schema(
            new_schema_file, "../dev.db" if environment == "dev" else "./test.db"
        )
    command = ["prisma", "db", "push", f"--schema={new_schema_file}"]
    subprocess.run(command)


def get_db_prisma_url():
    load_dotenv()
    db_prisma_url = os.environ.get("DB_PRISMA_URL").split("?")[0]
    return db_prisma_url


def run_scripts(db_path: str):
    for filename in os.listdir("db/scripts"):
        if filename.endswith(".sql"):
            filepath = os.path.join("db/scripts", filename)
            with open(filepath, "r") as file:
                sql_script = file.read()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()
            print(f"Executed {filename}")
