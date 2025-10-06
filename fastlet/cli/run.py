import subprocess
import typer

from ..utils.db import push_to_db, run_scripts, get_db_prisma_url
from ..utils.settings import get_settings

import os
import psycopg
from enum import Enum

app = typer.Typer()


class DevStag(Enum):
    DEV = "dev"
    STAG = "stag"

class TestDevStag(Enum):
    TEST = "test"
    DEV = "dev"
    STAG = "stag"

@app.command()
def ide(environment: DevStag):
    """Open Harlequin IDE"""
    if environment.value == "stag":
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
def push(environment: TestDevStag):
    """Push Prisma schema"""
    push_to_db(environment.value)


@app.command()
def scripts(environment: DevStag):
    """Run SQL scripts on DB."""
    if environment.value == "stag":
        settings = get_settings("service_with_db")

        for filename in os.listdir("db/scripts"):
            if filename.endswith(".sql"):
                filepath = os.path.join("db/scripts", filename)
                with open(filepath, "r") as file:
                    sql_script = (
                        f"SET search_path TO {settings.db_schema};{file.read()}"
                    )
                conn = psycopg.connect(get_db_prisma_url())
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

def export_file(name: str, export_dir: str = ".", src_dir: str = None, mode: Literal["w", "a"] = "w"):
    """Export file from this module to a target directory and add to Git tracking."""
    src_path = src_dir if src_dir else __file__
    src = os.path.join(os.path.dirname(src_path), "files", name)
    dest = os.path.join(export_dir, name)

    if os.path.exists(src):
        os.makedirs(export_dir, exist_ok=True)
        with open(src, "r") as file:
            content = file.read()
        with open(dest, "w") as file:
            file.write(content)
        print(f"{name} exported to {export_dir}.")

        # Try to add the exported file to Git tracking
        try:
            subprocess.run(["git", "add", dest], check=True)
            print(f"{name} added to Git tracking.")
        except subprocess.CalledProcessError:
            print(f"Failed to add {name} to Git. Are you in a Git repo?")
    else:
        print(f"{name} not found in the module directory.")

@app.command()
def start():
    export_file("Dockerfile")
    export_file("pytest.ini")
    export_file("requirements-base.txt")
    export_file("requirements-dev.txt")
    export_file("ci.yml", ".github/workflows")

def main():
    app()
