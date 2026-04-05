# Fastlet

Unified framework for building FastAPI services. Wraps crotal (auth), piping_bag (DB migrations + codegen), and pyopenapi-gen (API client generation). All service-level imports go through fastlet — never import from the underlying libraries directly.

## Install

```bash
# Without database
pip install "fastlet @ git+https://github.com/draew6/fastlet2.git"

# With database (includes piping_bag + asyncpg)
pip install "fastlet[db] @ git+https://github.com/draew6/fastlet2.git"

# With email (includes resend)
pip install "fastlet[mail] @ git+https://github.com/draew6/fastlet2.git"
```

## Env vars

```
# Auth (always required)
AUTH_LOGIN_URL=
JWT_SECRET=
COOKIE_SECRET=
ROOT_DOMAIN=

# Database (only with fastlet[db])
DATABASE_URL=

# Mail (only with fastlet[mail])
RESEND_API_KEY=
```

Generate a template with `fastlet env`.

## Rules

- NEVER import from crotal, piping_bag, or pyopenapi-gen directly — always import from fastlet
- NEVER write custom auth middleware — use fastlet's auth dependencies (User, Admin, etc.)
- NEVER manage DB connection pools manually — use `setup(app)` or `init_pool()`/`close_pool()`
- NEVER write httpx clients for service-to-service calls — use `BaseClient` + `service()` + generated clients
- NEVER generate API clients manually — use `fastlet client generate`
- NEVER write DB migrations by hand — use `fastlet db` commands
- NEVER define routers manually when the convention is file-based — use `autoload(app, "routes")`
- ALWAYS use `create_client` for forwarding user tokens, `create_system_client` for service-to-service tokens
- ALWAYS close service clients — use the dependency pattern (handles it automatically) or `async with`

## Auth

All re-exported from crotal. Always import from fastlet:

```python
from fastlet import User, OptionalUser, Admin, System, AdminOrSelf, SystemOrSelf, MustBeSelf
from fastlet import UserInfo, AuthTokens
```

### Endpoint protection

```python
@app.get("/profile")
async def get_profile(user: User):
    return {"id": user.id, "name": user.name, "role": user.role}

@app.get("/admin")
async def admin_only(user: Admin): ...

@app.get("/users/{user_id}")
async def get_user(user_id: int, user: AdminOrSelf): ...
```

### Tokens (for auth services only, not for regular services)

```python
from fastlet import create_access_token, create_system_access_token, create_token
```

### Cookies

```python
from fastlet import set_cookie

@app.post("/login")
async def login(response: Response):
    set_cookie(response, "access_token", token)
```

### Testing

```python
from fastlet import authenticated_client
from starlette.testclient import TestClient

client = authenticated_client(TestClient(app), id=5, name="alice", role="ADMIN")
```

## Database

Requires `fastlet[db]`. Wraps piping_bag (asyncpg + pgschema + sqlc).

### Setup

```python
from fastlet import setup

app = FastAPI()
setup(app)  # manages asyncpg pool lifecycle
```

### Using generated queries

After running `fastlet db up`, a `QueriesDep` is auto-generated in `db/__init__.py`:

```python
from db import QueriesDep

@app.get("/users")
async def get_users(queries: QueriesDep):
    return await queries.list_users()
```

### DB workflow

1. Edit `db/schema.sql` (source of truth)
2. Write queries in `db/queries/*.sql` with sqlc annotations
3. Run `fastlet db up` (applies migration + generates Python client)

### CLI commands

| Command | What it does |
|---|---|
| `fastlet db up` | Apply migration + generate client (most common) |
| `fastlet db plan` | Preview migration without applying |
| `fastlet db apply` | Apply migration only |
| `fastlet db generate` | Generate Python client only |
| `fastlet db sync` | Plan + apply in one step |
| `fastlet db dump` | Dump live DB schema to db/schema.sql |
| `fastlet db diff` | Show planned changes |
| `fastlet db studio` | Open Prisma Studio |
| `fastlet db sql` | Open Harlequin SQL IDE |

### Query file format (sqlc)

```sql
-- name: GetUser :one
SELECT * FROM users WHERE id = $1;

-- name: ListUsers :many
SELECT * FROM users ORDER BY created_at DESC LIMIT $1;

-- name: CreateUser :one
INSERT INTO users (email, name) VALUES ($1, $2) RETURNING *;
```

## Service client (service-to-service calls)

### 1. Generate client from OpenAPI spec

```bash
fastlet client generate users-api.yaml
fastlet client generate posting-api.yaml
```

Generates typed async clients into `client/<spec_name>/`.

### 2. Define unified client

```python
# dependencies.py
from fastlet import BaseClient, service, create_client, create_system_client
from client.users_api.client import APIClient as UsersClient
from client.posting_api.client import APIClient as PostingClient


class APIClient(BaseClient):
    def __init__(self):
        self.users = service(UsersClient, "https://users.api")
        self.posting = service(PostingClient, "https://posting.api")


# Forwards caller's Bearer token to downstream services
Client = create_client(APIClient)

# Uses system access token (via crotal) for service-to-service calls
SystemClient = create_system_client(APIClient)
```

### 3. Use in routes

```python
from dependencies import Client, SystemClient

@router.get("/users")
async def list_users(client: Client):
    return await client.users.list_users(limit=10)

@router.post("/sync")
async def sync_data(client: SystemClient):
    return await client.users.list_users()
```

### Client internals

- `service(ClientClass, base_url, timeout=30)` — creates typed client instance, auto-discovers config from generated module
- `BaseClient` — unifies multiple services, provides `set_access_token()` and `set_service_token()`
- `create_client(APIClient)` — FastAPI dependency that forwards Bearer token from incoming request
- `create_system_client(APIClient)` — FastAPI dependency that creates system token via crotal
- Both handle lifecycle automatically (created per request, closed after response)
- Downstream HTTP errors are re-raised as `HTTPException` with matching status code

## Router autoloading

```python
from fastlet import autoload

app = FastAPI()
autoload(app, "routes")
```

Recursively scans `routes/` and subpackages. Any module with a `router` attribute gets auto-included. File structure becomes the URL structure.

## CORS

```python
from fastlet import allow_cors

allow_cors(app)
```

Allows all subdomains of `ROOT_DOMAIN` + `http://localhost:8001` for local dev.

## Mail

Requires `fastlet[mail]`.

```python
from fastlet.mail import send_mail

await send_mail(
    address_from="noreply@example.com",
    addresses_to=["user@example.com"],
    subject="Welcome",
    html_content="<h1>Hello</h1>",
)
```

## Typical service structure

```
my-service/
  .env
  interface/
    api.py              # FastAPI app, setup, autoload
  routes/
    users.py            # router with endpoints
    admin.py
  dependencies.py       # APIClient, Client, SystemClient
  db/
    schema.sql          # DB schema (source of truth)
    queries/            # sqlc query files
      users.sql
    generated/          # auto-generated by fastlet db generate
    __init__.py         # auto-generated QueriesDep
  client/
    users_api/          # auto-generated by fastlet client generate
    posting_api/
  CLAUDE.md
```

## Architecture

Fastlet is a thin re-export layer with lazy imports:

- `fastlet.auth` — re-exports from crotal (User, Admin, tokens, cookies, testing)
- `fastlet.db` — re-exports from piping_bag (pool management, query dependencies)
- `fastlet.client` — BaseClient, service(), create_client, create_system_client (original code)
- `fastlet.mail` — send_mail via resend (original code)
- `fastlet.cli` — wraps `pb` and `pyopenapi-gen` CLI commands

`__init__.py` uses `__getattr__` for lazy loading — submodules only import when accessed.