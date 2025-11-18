# AGENTS.md
> **Scope:** These instructions tune our **Codex** code-generation agent (LLM via API/CLI) for this monorepo. They are **authoritative**: follow them over generic best practices. Output must compile, pass linters/tests, and fit our structure.

---

## 1) Repository at a glance

* **Monorepo:** Python backends + Vue 3/TypeScript frontend.
* **Structure:**

  * `libs/` – reusable Python packages (APIs, domain/services, repositories, schemas, utils)
  * `services/` – thin Python apps composing `libs`; Vue/Nx frontend
  * `infrastructure/` – Helm/Tilt/K3d, Terraform, values under `infrastructure/rag/values.yaml`
  * `docs/` – docs & UI customization
* **Config:** Env-driven via `.env` (dev tooling only). Never hardcode secrets.

> **Rule of thumb:** Business logic lives in **`libs`**. **`services`** only do bootstrapping, DI, routing, and wiring.

---

## 2) Languages & toolchain

* **Python:** 3.13, **FastAPI**, **Pydantic v2**, **Poetry**
* **Style/Quality:** `black` (line length **120**), `isort` (profile `black`), `flake8` (plugins), NumPy docstrings, type hints (PEP 484), absolute imports only
* **Testing:** `pytest` (+ coverage), optional `pytest-asyncio` for async code
* **Frontend:** Vue 3, TypeScript, Vite, Nx, Tailwind, Pinia, Vue I18n (Vitest + Cypress; ESLint)

---

## 3) Codex behavior (important)

* **Do not invent** secrets/URLs/paths. Use placeholders and `TODO:` comments.
* **Prefer libs over services:** Add APIs/logic in `libs/*`, wire in `services/*` (keep `main.py` thin: app import + container registration).
* **Always emit tests** with new Python code (≥1 happy path + ≥1 edge case). Keep unit tests isolated and fast.
* **Ask via comments if uncertain:** Start the diff with a short `# Assumptions:` block.
* **Respect performance & readability:** Small cohesive functions, avoid deep nesting/complexity.

---

## 4) Output contract

When asked to modify or add code, follow **one** of these formats:

* **Single file (new):**

  ```md
  ## path: libs/<pkg>/src/<pkg>/module.py
  ```

  ```python
  # file content here
  ```

* **Single file (edit):** provide a **unified diff**:

  ```diff
  --- a/libs/<pkg>/src/<pkg>/module.py
  +++ b/libs/<pkg>/src/<pkg>/module.py
  @@
  - old line
  + new line
  ```

* **Multiple files:** repeat the above per file, in logical order (libs first, then services, then tests).

* **Test plan:** end with a short block:

  ```txt
  Build/Test
  - poetry install
  - pytest -q --maxfail=1 --cov
  - black . && isort . && flake8
  ```

---

## 5) Python specifics

### Typing & style

* Use modern typing (`list[str]`, `dict[str, Any]`), avoid `Any` unless necessary.
* NumPy-style docstrings for public APIs. No wildcard imports. **Absolute imports only.**

### FastAPI

* Endpoints are **thin**; DI via `Depends`/container; no business logic in routers.
* Every route defines `response_model=...` and sanitizes outputs.
* Centralize exception mapping; never leak stack traces in prod.
* Prefer **async** endpoints for I/O-bound work.

### Validation & config

* **Pydantic v2**: use `field_validator`/`model_validator`; strict models at boundaries.
* **Configuration:** use `pydantic-settings` for environment-driven settings. `.env` is dev-only (Tilt/tests). Do not auto-load `.env` in production app code.

### HTTP & concurrency

* Use `httpx.AsyncClient` with explicit timeouts and retry/backoff. No `requests` in async code.
* Never use `time.sleep()`; use `asyncio.sleep()` (or anyio) in async contexts.

### Repositories & services

* Repositories are ports/adapters for DB/HTTP/queues. Services depend on repositories; routers depend on services.
* Transactions via context manager; avoid autocommit. Do not use raw SQL with f-strings.

### Logging

* Use `logging` (or `structlog`) with structured/contextual fields (`event`, `service`, `request_id`). No PII/secrets in logs.

### File layout for new Python code

* `libs/<package>/src/<package>/...` → APIs, services, repositories, schemas, utils
* `libs/<package>/tests/` → tests for the above
* `services/<service>/` → bootstrap, DI container, runtime config

---

## 6) Testing

* `pytest` with fixtures and mocks (`unittest.mock`, `pytest-mock`). No real network in unit tests; mock `httpx` (e.g., `respx`).
* Aim for **high coverage on core libs**. Mark slow tests with `@pytest.mark.slow`.
* Suggested `pytest.ini`:

  ```ini
  [pytest]
  addopts = -q --strict-markers --strict-config --maxfail=1 --cov=libs --cov-report=term-missing
  markers =
      slow: marks tests as slow (deselect with '-m "not slow"')
  asyncio_mode = strict
  ```

---

## 7) Frontend quick rules

* Use `<script setup lang="ts">` + Composition API. Strong typing (avoid `any`).
* State with **Pinia**; i18n with **Vue I18n**. Keep components small/presentational; move logic to composables/stores.
* Use Tailwind utilities; avoid inline styles. Unit tests with **Vitest**; E2E with **Cypress**.
* Use tsconfig path aliases (e.g., `@shared/utils`); expose stable public APIs via `index.ts` in libs.

---

## 8) Anti‑patterns (forbidden)

* Business logic in FastAPI routers or Vue components
* Relative imports; wildcard imports; raw SQL with f-strings
* `requests` in async code; `time.sleep()` in app/tests
* Logging secrets/PII; exposing stack traces to clients

---

## 9) Examples Codex should imitate

**Pydantic v2 model (NumPy docstring):**

```python
"""
User model.

Parameters
----------
id : str
    User ID.
name : str
    Full name.
active : bool
    Whether the user is active.
"""
from pydantic import BaseModel, field_validator

class User(BaseModel):
    id: str
    name: str
    active: bool = True

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v
```

**Router + DI outline (service stays thin):**

```python
from fastapi import APIRouter, Depends
from .schemas import User
from ..services.user_service import UserService
from ..container import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[User])
async def list_users(svc: UserService = Depends(get_user_service)):
    return await svc.list_users()
```

**httpx AsyncClient (timeouts + retry/backoff skeleton):**

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

DEFAULT_TIMEOUT = httpx.Timeout(5.0, connect=2.0)

@retry(wait=wait_exponential(multiplier=0.2, max=5), stop=stop_after_attempt(3))
async def fetch_json(url: str) -> dict:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
```

---

## 10) Review & quality gates

* Python: run `black`, `isort`, `flake8`, and `pytest --cov` before PR.
* Frontend: run ESLint + Vitest; add Cypress flows as needed.
* Keep PRs small and focused; update docs and `.env.template` when adding config.

---

## 11) Handy prompts for this repo

* "Create a router in `libs/rag-core-api` for collections (list/create/delete) and wire it in `services/rag-backend`."
* "Add Pydantic settings for S3 credentials and inject into the admin backend repository."
* "Generate a Vue component using Pinia that renders chat messages and emits an event on send, with Vitest tests."

---

## 12) Quick checklist (for every Codex suggestion)

* ✅ Fits `libs/` vs `services/` boundaries and file layout
* ✅ Compiles and passes linters (black/isort/flake8) and tests
* ✅ Uses Pydantic v2, FastAPI DI, httpx async
* ✅ No secrets/PII in code or logs; no stack traces in client responses
