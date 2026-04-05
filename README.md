# Fastlet

Unified framework for building FastAPI services. Wraps [crotal](https://github.com/draew6/crotal) (auth), [piping_bag](https://github.com/draew6/piping_bag) (DB), and [pyopenapi-gen](https://github.com/draew6/pyopenapi_gen) (API clients).

## Install

```bash
# Without database
pip install "fastlet @ git+https://github.com/draew6/fastlet2.git"

# With database
pip install "fastlet[db] @ git+https://github.com/draew6/fastlet2.git"
```

## Quick start

```python
from fastapi import FastAPI
from fastlet import User, Admin, autoload, allow_cors

app = FastAPI()
allow_cors(app)
autoload(app, "routes")

# routes/users.py
from fastapi import APIRouter
from fastlet import User

router = APIRouter()

@router.get("/profile")
async def get_profile(user: User):
    return {"id": user.id, "name": user.name}
```

## What's included

| Import from fastlet | Source | What it does |
|---|---|---|
| `User`, `Admin`, `System`, `OptionalUser` | crotal | Auth dependencies |
| `AdminOrSelf`, `SystemOrSelf`, `MustBeSelf` | crotal | Self-or-privileged access |
| `authenticated_client` | crotal | Test helper |
| `setup`, `get_pool`, `create_queries_dependency` | piping_bag | DB pool + query deps |
| `BaseClient`, `service`, `create_client` | fastlet | Service-to-service calls |
| `autoload` | fastlet | File-based router loading |
| `allow_cors` | fastlet | CORS from ROOT_DOMAIN |

## CLI

```bash
fastlet env                         # Generate .env template
fastlet db up                       # Apply migration + generate client
fastlet client generate spec.yaml   # Generate typed API client
```

## Documentation

See [CLAUDE.md](./CLAUDE.md) for detailed usage patterns, rules, and architecture.