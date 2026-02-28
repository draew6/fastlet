import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer()
db_app = typer.Typer(help="Database migrations and codegen (wraps pb).")
client_app = typer.Typer(help="API client generation (wraps pyopenapi-gen).")
app.add_typer(db_app, name="db")
app.add_typer(client_app, name="client")

_AUTH_VARS = [
    "AUTH_LOGIN_URL",
    "JWT_SECRET",
    "COOKIE_SECRET",
    "ROOT_DOMAIN",
]

_DB_VARS = [
    "DATABASE_URL",
]


@app.command()
def env() -> None:
    """Create a .env file with all required environment variables."""
    path = Path(".env")
    if path.exists():
        typer.confirm(".env already exists. Overwrite?", abort=True)

    lines = ["# Auth (crotal)"]
    lines.extend(f"{var}=" for var in _AUTH_VARS)
    lines.append("")
    lines.append("# Database (piping_bag) — only needed with fastlet[db]")
    lines.extend(f"{var}=" for var in _DB_VARS)
    lines.append("")

    path.write_text("\n".join(lines))
    typer.echo(f"Created {path}")


@client_app.command()
def generate(
    spec: str = typer.Argument(help="Path or URL to OpenAPI spec"),
    project_root: str = typer.Option(".", help="Directory containing top-level Python packages"),
    output_package: str | None = typer.Option(None, help="Python package path for generated client (default: client.<spec_name>)"),
    core_package: str | None = typer.Option(None, help="Python package path for shared core"),
    naming_strategy: str = typer.Option("clean", help="Naming strategy: operationId, clean, or path"),
    force: bool = typer.Option(False, help="Skip diff checks before overwriting"),
    no_postprocess: bool = typer.Option(False, help="Skip Black formatting and mypy checking"),
    verbose: bool = typer.Option(False, help="Show detailed progress"),
) -> None:
    """Generate a typed async API client from an OpenAPI spec."""
    if output_package is None:
        stem = Path(spec).stem.replace("-", "_").replace(".", "_")
        output_package = f"client.{stem}"
    cmd = ["pyopenapi-gen", spec, "--project-root", project_root, "--output-package", output_package]
    if core_package:
        cmd.extend(["--core-package", core_package])
    cmd.extend(["--naming-strategy", naming_strategy])
    if force:
        cmd.append("--force")
    if no_postprocess:
        cmd.append("--no-postprocess")
    if verbose:
        cmd.append("--verbose")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def _run_pb(subcommand: str) -> None:
    result = subprocess.run(["pb", subcommand])
    sys.exit(result.returncode)


@db_app.command()
def init() -> None:
    """Initialize the database project scaffold."""
    _run_pb("init")


@db_app.command()
def plan() -> None:
    """Plan pending migrations."""
    _run_pb("plan")


@db_app.command()
def apply() -> None:
    """Apply pending migrations."""
    _run_pb("apply")


@db_app.command()
def sync() -> None:
    """Sync the database schema."""
    _run_pb("sync")


@db_app.command()
def generate() -> None:
    """Generate typed query code."""
    _run_pb("generate")


@db_app.command()
def up() -> None:
    """Migrate and generate (plan + apply + generate)."""
    _run_pb("up")


@db_app.command()
def dump() -> None:
    """Dump the current database schema."""
    _run_pb("dump")


@db_app.command()
def diff() -> None:
    """Show schema diff."""
    _run_pb("diff")


@db_app.command()
def studio() -> None:
    """Open Prisma Studio."""
    _run_pb("studio")


@db_app.command()
def sql() -> None:
    """Open Harlequin SQL IDE."""
    _run_pb("sql")
