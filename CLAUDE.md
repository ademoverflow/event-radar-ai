# CLAUDE.md - AI Assistant Guide

This document provides essential context for AI assistants working with this codebase.

## Project Overview

Full-stack monorepo with:
- **Backend**: Python 3.13+ / FastAPI
- **Frontend**: TypeScript / React 19 / Vite
- **Database**: PostgreSQL 17
- **Containerization**: Docker Compose

## Code Quality Standards

### Python (Ruff + MyPy)

Configuration in `/pyproject.toml`:
- Line length: 100 characters
- Indent: 4 spaces
- Quote style: double quotes
- All rules enabled with specific ignores (see `[tool.ruff.lint]`)

```bash
poe check_format   # Check formatting
poe fix_format     # Fix formatting
poe check_lint     # Run linting
poe check_sort     # Check import order
poe fix_sort       # Fix import order
poe type_check     # Run mypy
```

### TypeScript/JavaScript (Biome)

Configuration in `/biome.json`:
- Tab indentation
- Double quotes
- Organize imports enabled

```bash
pnpm lint          # Run linter
pnpm format        # Run formatter
pnpm check         # Run both
```

### Commit Messages

Conventional commits enforced via commitlint. Format: `type(scope): description`

Allowed types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`, `wip`

## Project Structure

```
/
├── core/                    # Python FastAPI backend
│   ├── src/core/
│   │   ├── __main__.py     # Entry point
│   │   ├── main.py         # FastAPI app setup
│   │   ├── settings.py     # Pydantic settings
│   │   ├── database.py     # Async SQLAlchemy setup
│   │   ├── routers/        # API route handlers
│   │   ├── models/         # SQLModel data models
│   │   ├── security/       # JWT + password hashing
│   │   ├── middlewares/    # Auth middleware
│   │   ├── logger/         # Structured logging
│   │   └── alembic/        # Database migrations
│   └── tests/
├── webapp/                  # React SPA frontend
│   └── src/
│       ├── main.tsx        # App bootstrap with router
│       ├── env.ts          # T3 Env configuration
│       ├── pages/          # Page components
│       └── integrations/   # Library integrations
├── scripts/                 # Development utilities
├── compose.yaml            # Docker orchestration
└── bootstrap.sh            # Project initialization
```

## Design Patterns

### Backend (Python/FastAPI)

**Router Pattern**:
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ResponseModel(BaseModel):
    field: str

@router.get("/endpoint", tags=["Tag"])
def handler() -> ResponseModel:
    return ResponseModel(field="value")
```

**SQLModel ORM**:
```python
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, UUID, text

class Model(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    )
```

**Async Database Session**:
```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session

async def handler(session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    ...
```

**Settings Management**:
```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Password Hashing** (Argon2id):
```python
from core.security.password import hash_password, verify_password
```

**JWT Tokens**:
```python
from core.security.token import create_access_token
from datetime import timedelta

token = create_access_token({"sub": user_id}, timedelta(minutes=60))
```

### Frontend (React/TypeScript)

**TanStack Router** (code-based):
```typescript
import { createRoute } from "@tanstack/react-router";

const route = createRoute({
    getParentRoute: () => rootRoute,
    path: "/path",
    component: Component,
});
```

**TanStack Query**:
```typescript
import { useQuery } from "@tanstack/react-query";

const { data } = useQuery({
    queryKey: ["key"],
    queryFn: () => fetch("/api/endpoint").then(r => r.json()),
});
```

**Environment Variables** (T3 Env + Zod):
```typescript
import { env } from "@/env";
// Only access validated env vars through this import
```

## Testing

### Python Tests
```bash
# Run from project root
uv run pytest core/tests/
```

Pattern: FastAPI TestClient with assertions
```python
from fastapi.testclient import TestClient
from core.main import app

client = TestClient(app)

def test_endpoint() -> None:
    response = client.get("/endpoint")
    assert response.status_code == 200
```

### JavaScript Tests
```bash
cd webapp && pnpm test
```

Framework: Vitest + Testing Library

## Development Workflow

### Starting Services
```bash
docker compose up
```

### Ports
| Service | Port |
|---------|------|
| Adminer | 8997 |
| Webapp  | 8998 |
| Core API| 8999 |

### Database Migrations
Migrations auto-run on startup via FastAPI lifespan. Manual commands:
```bash
# Inside core container or with uv
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Key Files Reference

| Purpose | File |
|---------|------|
| FastAPI app | `core/src/core/main.py` |
| Settings | `core/src/core/settings.py` |
| Database | `core/src/core/database.py` |
| User model | `core/src/core/models/user.py` |
| Auth middleware | `core/src/core/middlewares/user.py` |
| React entry | `webapp/src/main.tsx` |
| Env validation | `webapp/src/env.ts` |
| Docker setup | `compose.yaml` |
| Python config | `pyproject.toml` |
| JS config | `biome.json` |
