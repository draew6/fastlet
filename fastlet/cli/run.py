import subprocess
import typer
from typing import Literal

from ..utils.db import push_to_db, run_scripts, get_db_prisma_url
from ..utils.settings import get_settings

import os
import psycopg


app = typer.Typer()


@app.command()
def ide(environment: Literal["dev", "stag"]):
    """Open Harlequin IDE"""
    if environment == "stag":
        settings = get_settings("service_with_db")
        command = [
            "harlequin",
            "-a",
            "postgres",
            "-h",
            settings.db_host,
            "-p",
            settings.db_port,
            "-U",
            settings.db_user,
            "--password",
            settings.db_password,
            "-d",
            settings.db_name,
            "-r",
        ]
    else:
        command = ["harlequin", "-a", "sqlite", "--mode", "rw", "db/dev.db"]

    subprocess.run(command)


@app.command()
def push(environment: Literal["test", "dev", "stag"]):
    """Push Prisma schema"""
    push_to_db(environment)


@app.command()
def scripts(environment: Literal["dev", "stag"]):
    """Run SQL scripts on DB."""
    if environment == "stag":
        settings = get_settings("service_with_db")

        for filename in os.listdir("db/scripts"):
            if filename.endswith(".sql"):
                filepath = os.path.join("db/scripts", filename)
                with open(filepath, "r") as file:
                    sql_script = (
                        f"SET search_path TO {settings.db_schema};{file.read()}"
                    )
                conn = psycopg.connect(dsn=get_db_prisma_url())
                cursor = conn.cursor()
                cursor.execute(sql_script)
                conn.commit()
                conn.close()
                print(f"Executed {filename}")
    else:
        run_scripts("db/internals/test.db")


@app.command()
def studio():
    """Open Prisma Studio."""
    command = ["prisma", "studio", "--schema=db/schema.prisma"]
    subprocess.run(command)


@app.command()
def secret():
    """Generate a new secret."""
    try:
        output = subprocess.check_output(["openssl", "rand", "-hex", "32"], text=True)
        print("Generated random hex string:")
        print(output.strip())
    except subprocess.CalledProcessError as e:
        print("Error running the command:", e)


def main():
    app()
