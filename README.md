# Fastlet

Unified wrapper for building FastAPI services with **crotal** (auth), **piping_bag** (DB migrations/codegen), and **pyopenapi-gen** (API client generation).

## Install

```bash
# Composite service (auth only, no database)
pip install "fastlet @ git+https://github.com/draew6/fastlet2.git"

# Core service (auth + database)
pip install "fastlet[db] @ git+https://github.com/draew6/fastlet2.git"
```

## Environment Variables

Generate a `.env` template:

```bash
fastlet env
```

This creates:

```env
# Auth (crotal)
AUTH_LOGIN_URL=
JWT_SECRET=
COOKIE_SECRET=
ROOT_DOMAIN=

# Database (piping_bag) — only needed with fastlet[db]
DATABASE_URL=
```

## Python API

### Auth (from crotal)

```python
from fastlet import User, OptionalUser, Admin, System
from fastlet import AdminOrSelf, SystemOrSelf, MustBeSelf
from fastlet import AuthTokens, UserInfo
from fastlet import create_token, create_access_token, create_system_access_token
from fastlet import authenticated_client  # testing helper
```

**Dependencies** — use as FastAPI endpoint parameters:

| Dependency | Description |
|---|---|
| `User` | Requires authenticated user |
| `OptionalUser` | Auth optional, returns `None` if missing |
| `Admin` | Requires admin role |
| `System` | Requires system role |
| `AdminOrSelf` | Admin, or user matching the resource |
| `SystemOrSelf` | System, or user matching the resource |
| `MustBeSelf` | User must match the resource |

**Tokens:**

- `create_access_token(user_id, name, role)` — JWT access token
- `create_system_access_token()` — system-level token
- `create_token(user_id, name, role)` — returns `AuthTokens` (access + refresh)

**Testing:**

```python
from fastlet import authenticated_client

client = authenticated_client(test_client, id=1, name="testuser", role="USER")
```

### Database (from piping_bag) — requires `fastlet[db]`

```python
from fastlet import setup, init_pool, close_pool, get_pool, create_queries_dependency
```

- `setup(app)` — attaches asyncpg pool lifecycle to FastAPI app
- `init_pool()` / `close_pool()` — manual pool management
- `get_pool()` — returns the current asyncpg pool
- `create_queries_dependency(QueriesClass)` — FastAPI dependency for generated query classes

### Router Autoloading

```python
from fastapi import FastAPI
from fastlet import autoload

app = FastAPI()
autoload(app, "routes")
```

Recursively scans `routes` and its subpackages. Any module with a `router` attribute gets auto-included via `app.include_router(module.router)`.

### CORS

```python
from fastlet import allow_cors

allow_cors(app)
```

Configures CORS using crotal's `ROOT_DOMAIN` env var. Allows all subdomains of `root_domain`, plus `http://localhost:8001` for local development.

## CLI

### `fastlet env`

Creates `.env` template with all required variables.

### `fastlet db <command>`

Wraps the `pb` CLI (piping_bag). Available commands:

| Command | Description |
|---|---|
| `fastlet db init` | Scaffold database project |
| `fastlet db plan` | Plan pending migrations |
| `fastlet db apply` | Apply pending migrations |
| `fastlet db sync` | Sync database schema |
| `fastlet db generate` | Generate typed Python query code |
| `fastlet db up` | Migrate + generate (plan + apply + generate) |
| `fastlet db dump` | Dump current schema |
| `fastlet db diff` | Show schema diff |
| `fastlet db studio` | Open Prisma Studio |
| `fastlet db sql` | Open Harlequin SQL IDE |

### `fastlet client generate`

Generates a typed async API client from an OpenAPI spec (wraps `pyopenapi-gen`).

```bash
# Generates into client/users_api/
fastlet client generate users-api.yaml
```

| Option | Default | Description |
|---|---|---|
| `SPEC` (argument) | required | Path or URL to OpenAPI spec |
| `--output-package` | `client.<spec_name>` | Python package path for generated client |
| `--project-root` | `.` | Directory containing top-level Python packages |
| `--core-package` | auto | Python package path for shared core |
| `--naming-strategy` | `clean` | `operationId`, `clean`, or `path` |
| `--force` | off | Skip diff checks before overwriting |
| `--no-postprocess` | off | Skip Black formatting and mypy checking |
| `--verbose` | off | Show detailed progress |

The generated client is standalone (no runtime dependency on pyopenapi-gen) and async-first.

### Service Client

**1. Generate clients from OpenAPI specs:**

```bash
fastlet client generate users-api.yaml
fastlet client generate posting-api.yaml
```

**2. Define your unified client** (`dependencies.py`):

```python
from fastlet import BaseClient, service, create_client, create_system_client
from client.users_api.client import APIClient as UsersClient
from client.posting_api.client import APIClient as PostingClient


class APIClient(BaseClient):
    def __init__(self):
        self.users = service(UsersClient, "https://users.api")
        self.posting = service(PostingClient, "https://posting.api")


# Forwards the caller's Bearer token
Client = create_client(APIClient)

# Uses a system access token (via crotal)
SystemClient = create_system_client(APIClient)
```

**3. Use in routes** (`routes/users.py`):

```python
from fastapi import APIRouter
from dependencies import Client, SystemClient

router = APIRouter()


@router.get("/users")
async def list_users(client: Client):
    return await client.users.list_users(limit=10)


@router.post("/sync")
async def sync_data(client: SystemClient):
    return await client.users.list_users()
```

- `service(ClientClass, base_url, timeout=30)` — creates a typed client instance, auto-discovers config from the generated module
- `BaseClient` — unifies multiple services, provides `set_access_token()` and `set_service_token()`
- `create_client(ClientClass)` — `Annotated` FastAPI dependency, forwards Bearer token from request
- `create_system_client(ClientClass)` — `Annotated` FastAPI dependency, creates system token via crotal
- Both handle lifecycle automatically (created per request, closed after response)
