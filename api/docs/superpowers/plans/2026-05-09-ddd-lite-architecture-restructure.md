# DDD-Lite Architecture Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the Babytroc API from layer-first (`models/`, `schemas/`, `services/`) to domain-first (`domains/item/`, `domains/chat/`, etc.) with composable query filters.

**Architecture:** Each domain becomes a self-contained package under `app/domains/` with its own models, schemas, filters, services, and errors. Infrastructure (DB, cache, pubsub, email, S3) moves to `app/infrastructure/`. Shared utilities (pagination, generic filters) move to `app/shared/`. Routers stay in `app/routers/` (HTTP delivery concern). Query param schemas move from domain schemas to router-adjacent `queries.py` files.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy async, Pydantic, PostgreSQL, Redis, pytest

**Spec:** `docs/superpowers/specs/2026-05-09-ddd-lite-architecture-restructure-design.md`

---

## Important Context

This is a mechanical restructure followed by targeted refactoring. The primary operation is moving files and updating import paths. ~170 source files and ~53 test files have imports that will change.

**Strategy:** Use `git mv` for moves (preserves history), then global find-and-replace for import paths. Work domain-by-domain. Run `mise run test` after each major task to catch breakage early.

**Branch:** All work on a new branch off `main`.

**Import rewriting convention:** When a file moves from `app/X/Y.py` to `app/domains/Z/Y.py`, every `from app.X.Y import ...` becomes `from app.domains.Z.Y import ...`. Use `sed` or IDE refactoring for bulk updates.

---

## Phase 1: Scaffold and Move Infrastructure

### Task 1: Create branch and directory structure

**Files:**
- Create: `app/domains/__init__.py`
- Create: `app/domains/{item,chat,loan,user,auth,image,region,category,report}/__init__.py`
- Create: `app/infrastructure/__init__.py`
- Create: `app/shared/__init__.py`

- [ ] **Step 1: Create the feature branch**

```bash
git checkout main
git pull
git checkout -b refactor/ddd-lite-restructure
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p app/domains/{item,chat,loan,user,auth,image,region,category,report}
mkdir -p app/infrastructure
mkdir -p app/shared
touch app/domains/__init__.py
touch app/domains/{item,chat,loan,user,auth,image,region,category,report}/__init__.py
touch app/infrastructure/__init__.py
touch app/shared/__init__.py
```

- [ ] **Step 3: Commit scaffold**

```bash
git add app/domains app/infrastructure app/shared
git commit -m "refactor: scaffold domains/, infrastructure/, shared/ directories"
```

---

### Task 2: Move infrastructure modules

Move the non-domain plumbing from `app/` root and `app/clients/` into `app/infrastructure/`.

**Files:**
- Move: `app/config.py` -> `app/infrastructure/config.py`
- Move: `app/database.py` -> `app/infrastructure/database.py`
- Move: `app/pubsub.py` -> `app/infrastructure/pubsub.py`
- Move: `app/email.py` -> `app/infrastructure/email.py`
- Move: `app/cache.py` -> `app/infrastructure/cache.py`
- Move: `app/cache_keys.py` -> `app/infrastructure/cache_keys.py`
- Move: `app/clients/cache.py` -> `app/infrastructure/cache_client.py`
- Move: `app/clients/redis.py` -> `app/infrastructure/redis.py`
- Move: `app/clients/storage/s3.py` -> `app/infrastructure/storage.py`
- Move: `app/clients/email/auth.py` -> `app/infrastructure/email_auth.py`
- Move: `app/clients/email/report.py` -> `app/infrastructure/email_report.py`
- Move: `app/clients/networking/` -> `app/infrastructure/networking/` (if still used)
- Modify: every file that imports from these old paths

- [ ] **Step 1: Move files with git mv**

```bash
git mv app/config.py app/infrastructure/config.py
git mv app/database.py app/infrastructure/database.py
git mv app/pubsub.py app/infrastructure/pubsub.py
git mv app/email.py app/infrastructure/email.py
git mv app/cache.py app/infrastructure/cache.py
git mv app/cache_keys.py app/infrastructure/cache_keys.py
git mv app/clients/cache.py app/infrastructure/cache_client.py
git mv app/clients/redis.py app/infrastructure/redis.py
git mv app/clients/storage/s3.py app/infrastructure/storage.py
git mv app/clients/email/auth.py app/infrastructure/email_auth.py
git mv app/clients/email/report.py app/infrastructure/email_report.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

To avoid touching 170+ files in one step, create thin re-exports at old paths so existing imports still work:

```python
# app/config.py
from app.infrastructure.config import *  # noqa: F401,F403
from app.infrastructure.config import Config, DatabaseConfig, RedisConfig, PubsubConfig, EmailConfig, S3Config, AuthConfig
```

```python
# app/database.py
from app.infrastructure.database import *  # noqa: F401,F403
```

```python
# app/pubsub.py
from app.infrastructure.pubsub import *  # noqa: F401,F403
```

```python
# app/email.py
from app.infrastructure.email import *  # noqa: F401,F403
```

```python
# app/cache.py
from app.infrastructure.cache import *  # noqa: F401,F403
```

```python
# app/cache_keys.py
from app.infrastructure.cache_keys import *  # noqa: F401,F403
```

```python
# app/clients/cache.py — recreate
from app.infrastructure.cache_client import *  # noqa: F401,F403
```

```python
# app/clients/redis.py — recreate
from app.infrastructure.redis import *  # noqa: F401,F403
```

Do the same for `app/clients/storage/s3.py` and `app/clients/email/`.

- [ ] **Step 3: Fix internal imports within moved infrastructure files**

The moved files import each other. Update these intra-infrastructure imports:

- `app/infrastructure/database.py`: if it imports from `app.pubsub`, change to `app.infrastructure.pubsub`
- `app/infrastructure/cache.py`: if it imports from `app.clients.cache`, change to `app.infrastructure.cache_client`
- `app/infrastructure/pubsub.py`: if it imports from `app.schemas.pubsub`, leave for now (schemas move later)
- `app/app.py`: update imports from `app.config`, `app.database`, `app.pubsub`, `app.email`, `app.cache`, `app.clients.cache`, `app.clients.redis` to use `app.infrastructure.*`

Check each moved file's own imports and fix them to reference `app.infrastructure.*` where the target has already moved.

- [ ] **Step 4: Run tests**

```bash
mise run test
```

All tests must pass. The compatibility re-exports ensure nothing breaks.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move infrastructure modules to app/infrastructure/"
```

---

### Task 3: Move shared utilities

**Files:**
- Move: `app/schemas/query.py` -> `app/shared/pagination.py`
- Move: `app/schemas/utils.py` -> `app/shared/utils.py`
- Move: `app/schemas/base.py` -> `app/shared/schemas.py`
- Move: `app/utils/hash.py` -> `app/shared/hash.py`
- Move: `app/utils/image.py` -> `app/shared/image.py`
- Move: `app/utils/pagination.py` -> `app/shared/pagination_utils.py` (or merge into `app/shared/pagination.py`)
- Move: `app/models/base.py` -> `app/shared/models.py`
- Create: `app/shared/filters.py` (empty for now, populated in Phase 2)

- [ ] **Step 1: Move files**

```bash
git mv app/schemas/query.py app/shared/pagination.py
git mv app/schemas/utils.py app/shared/utils.py
git mv app/schemas/base.py app/shared/schemas.py
git mv app/utils/hash.py app/shared/hash.py
git mv app/utils/image.py app/shared/image.py
git mv app/utils/pagination.py app/shared/pagination_utils.py
git mv app/models/base.py app/shared/models.py
touch app/shared/filters.py
```

- [ ] **Step 2: Create compatibility re-exports**

```python
# app/schemas/query.py
from app.shared.pagination import *  # noqa: F401,F403

# app/schemas/utils.py
from app.shared.utils import *  # noqa: F401,F403

# app/schemas/base.py
from app.shared.schemas import *  # noqa: F401,F403

# app/utils/hash.py
from app.shared.hash import *  # noqa: F401,F403

# app/utils/image.py
from app.shared.image import *  # noqa: F401,F403

# app/utils/pagination.py
from app.shared.pagination_utils import *  # noqa: F401,F403

# app/models/base.py
from app.shared.models import *  # noqa: F401,F403
```

- [ ] **Step 3: Fix internal imports in moved files**

- `app/shared/models.py`: likely standalone (SQLAlchemy only), no changes expected
- `app/shared/pagination.py` (was `schemas/query.py`): check if it imports from `app.schemas.base` and update to `app.shared.schemas`
- `app/shared/utils.py` (was `schemas/utils.py`): likely standalone

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move shared utilities to app/shared/"
```

---

## Phase 2: Move Domains (one per task)

Each task moves one domain's models, errors, schemas, and services into `app/domains/{name}/`. The pattern is identical for each domain, so we describe it fully for `item` (the most complex), then list the specifics for each subsequent domain.

### Task 4: Move the Item domain

**Files:**
- Move: `app/models/item/` (item.py, image.py, category.py, region.py, like.py, save.py) -> `app/domains/item/models/`
- Move: `app/errors/item.py`, `app/errors/like.py`, `app/errors/save.py` -> `app/domains/item/errors.py` (merge)
- Move: `app/schemas/item/` -> `app/domains/item/schemas/`
- Move: `app/services/item/` -> `app/domains/item/services/`
- Move: `app/services/item/cache.py` -> `app/domains/item/cache.py`

- [ ] **Step 1: Move models**

```bash
mkdir -p app/domains/item/models
git mv app/models/item/item.py app/domains/item/models/item.py
git mv app/models/item/image.py app/domains/item/models/image.py
git mv app/models/item/category.py app/domains/item/models/category.py
git mv app/models/item/region.py app/domains/item/models/region.py
git mv app/models/item/like.py app/domains/item/models/like.py
git mv app/models/item/save.py app/domains/item/models/save.py
git mv app/models/item/__init__.py app/domains/item/models/__init__.py
```

Create re-export at old location:

```python
# app/models/item/__init__.py (recreate)
from app.domains.item.models import *  # noqa: F401,F403
```

- [ ] **Step 2: Move errors**

```bash
git mv app/errors/item.py app/domains/item/errors.py
```

If `app/errors/like.py` and `app/errors/save.py` exist and are item-specific, merge their contents into `app/domains/item/errors.py`.

Create re-exports:

```python
# app/errors/item.py (recreate)
from app.domains.item.errors import *  # noqa: F401,F403

# app/errors/like.py (recreate if merged)
from app.domains.item.errors import *  # noqa: F401,F403

# app/errors/save.py (recreate if merged)
from app.domains.item.errors import *  # noqa: F401,F403
```

- [ ] **Step 3: Move schemas**

```bash
mkdir -p app/domains/item/schemas
git mv app/schemas/item/base.py app/domains/item/schemas/base.py
git mv app/schemas/item/create.py app/domains/item/schemas/create.py
git mv app/schemas/item/update.py app/domains/item/schemas/update.py
git mv app/schemas/item/read.py app/domains/item/schemas/read.py
git mv app/schemas/item/preview.py app/domains/item/schemas/preview.py
git mv app/schemas/item/constants.py app/domains/item/schemas/constants.py
git mv app/schemas/item/api.py app/domains/item/schemas/api.py
git mv app/schemas/item/query.py app/domains/item/schemas/query.py
git mv app/schemas/item/__init__.py app/domains/item/schemas/__init__.py
```

Create re-export:

```python
# app/schemas/item/__init__.py (recreate if needed)
from app.domains.item.schemas import *  # noqa: F401,F403
```

- [ ] **Step 4: Move services**

```bash
mkdir -p app/domains/item/services
# Move all service files preserving structure
git mv app/services/item/create.py app/domains/item/services/create.py
git mv app/services/item/update.py app/domains/item/services/update.py
git mv app/services/item/delete.py app/domains/item/services/delete.py
git mv app/services/item/report.py app/domains/item/services/report.py
git mv app/services/item/cache.py app/domains/item/services/cache.py
git mv app/services/item/__init__.py app/domains/item/services/__init__.py

# Nested read/
mkdir -p app/domains/item/services/read
git mv app/services/item/read/get.py app/domains/item/services/read/get.py
git mv app/services/item/read/list.py app/domains/item/services/read/list.py
git mv app/services/item/read/selections.py app/domains/item/services/read/selections.py
git mv app/services/item/read/user_sets.py app/domains/item/services/read/user_sets.py
git mv app/services/item/read/__init__.py app/domains/item/services/read/__init__.py

# Nested like/
mkdir -p app/domains/item/services/like
git mv app/services/item/like/create.py app/domains/item/services/like/create.py
git mv app/services/item/like/delete.py app/domains/item/services/like/delete.py
git mv app/services/item/like/__init__.py app/domains/item/services/like/__init__.py

# Nested save/
mkdir -p app/domains/item/services/save
git mv app/services/item/save/create.py app/domains/item/services/save/create.py
git mv app/services/item/save/delete.py app/domains/item/services/save/delete.py
git mv app/services/item/save/__init__.py app/domains/item/services/save/__init__.py
```

Create re-export:

```python
# app/services/item/__init__.py (recreate)
from app.domains.item.services import *  # noqa: F401,F403
```

- [ ] **Step 5: Fix internal imports within moved item domain files**

Within `app/domains/item/`, update imports that reference old paths:
- `from app.models.item.item import Item` -> `from app.domains.item.models.item import Item`
- `from app.models.item.like import ItemLike` -> `from app.domains.item.models.like import ItemLike`
- `from app.schemas.item.create import ...` -> `from app.domains.item.schemas.create import ...`
- `from app.errors.item import ...` -> `from app.domains.item.errors import ...`
- `from app.services.item.read import ...` -> `from app.domains.item.services.read import ...`
- `from app.services.item.cache import ...` -> `from app.domains.item.services.cache import ...`

Cross-domain imports (e.g., `from app.services.user.star` in item create) can stay pointing to `app.services.user.*` for now — they'll resolve via re-exports until that domain moves.

- [ ] **Step 6: Run tests**

```bash
mise run test
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: move item domain to app/domains/item/"
```

---

### Task 5: Move the User domain

**Files:**
- Move: `app/models/user.py` -> `app/domains/user/models.py`
- Move: `app/errors/user.py` -> `app/domains/user/errors.py`
- Move: `app/schemas/user/` -> `app/domains/user/schemas/`
- Move: `app/services/user/` -> `app/domains/user/services/`
- Move: `app/domain/star.py` -> `app/domains/user/star.py`

- [ ] **Step 1: Move files**

```bash
git mv app/models/user.py app/domains/user/models.py
git mv app/errors/user.py app/domains/user/errors.py

mkdir -p app/domains/user/schemas
git mv app/schemas/user/base.py app/domains/user/schemas/base.py
git mv app/schemas/user/create.py app/domains/user/schemas/create.py
git mv app/schemas/user/update.py app/domains/user/schemas/update.py
git mv app/schemas/user/read.py app/domains/user/schemas/read.py
git mv app/schemas/user/preview.py app/domains/user/schemas/preview.py
git mv app/schemas/user/private.py app/domains/user/schemas/private.py
git mv app/schemas/user/constants.py app/domains/user/schemas/constants.py
git mv app/schemas/user/query.py app/domains/user/schemas/query.py
git mv app/schemas/user/__init__.py app/domains/user/schemas/__init__.py

mkdir -p app/domains/user/services/star
git mv app/services/user/create.py app/domains/user/services/create.py
git mv app/services/user/read.py app/domains/user/services/read.py
git mv app/services/user/update.py app/domains/user/services/update.py
git mv app/services/user/delete.py app/domains/user/services/delete.py
git mv app/services/user/report.py app/domains/user/services/report.py
git mv app/services/user/cache.py app/domains/user/services/cache.py
git mv app/services/user/star/update.py app/domains/user/services/star/update.py
git mv app/services/user/star/__init__.py app/domains/user/services/star/__init__.py
git mv app/services/user/__init__.py app/domains/user/services/__init__.py

git mv app/domain/star.py app/domains/user/star.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

Same pattern as Task 4 — recreate `app/models/user.py`, `app/errors/user.py`, `app/schemas/user/__init__.py`, `app/services/user/__init__.py`, `app/domain/star.py` as thin re-exports.

- [ ] **Step 3: Fix internal imports within moved user domain files**

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move user domain to app/domains/user/"
```

---

### Task 6: Move the Chat domain

**Files:**
- Move: `app/models/chat.py` -> `app/domains/chat/models.py`
- Move: `app/errors/chat.py` -> `app/domains/chat/errors.py`
- Move: `app/schemas/chat/` -> `app/domains/chat/schemas/`
- Move: `app/schemas/pubsub.py` -> `app/domains/chat/schemas/pubsub.py`
- Move: `app/schemas/websocket.py` -> `app/domains/chat/schemas/websocket.py`
- Move: `app/services/chat/` -> `app/domains/chat/services/`

- [ ] **Step 1: Move files**

```bash
git mv app/models/chat.py app/domains/chat/models.py
git mv app/errors/chat.py app/domains/chat/errors.py

mkdir -p app/domains/chat/schemas
git mv app/schemas/chat/base.py app/domains/chat/schemas/base.py
git mv app/schemas/chat/create.py app/domains/chat/schemas/create.py
git mv app/schemas/chat/read.py app/domains/chat/schemas/read.py
git mv app/schemas/chat/send.py app/domains/chat/schemas/send.py
git mv app/schemas/chat/api.py app/domains/chat/schemas/api.py
git mv app/schemas/chat/query.py app/domains/chat/schemas/query.py
git mv app/schemas/pubsub.py app/domains/chat/schemas/pubsub.py
git mv app/schemas/websocket.py app/domains/chat/schemas/websocket.py

mkdir -p app/domains/chat/services/chat
mkdir -p app/domains/chat/services/message
git mv app/services/chat/chat/create.py app/domains/chat/services/chat/create.py
git mv app/services/chat/chat/read.py app/domains/chat/services/chat/read.py
git mv app/services/chat/chat/report.py app/domains/chat/services/chat/report.py
git mv app/services/chat/chat/__init__.py app/domains/chat/services/chat/__init__.py
git mv app/services/chat/message/create.py app/domains/chat/services/message/create.py
git mv app/services/chat/message/read.py app/domains/chat/services/message/read.py
git mv app/services/chat/message/update.py app/domains/chat/services/message/update.py
git mv app/services/chat/message/__init__.py app/domains/chat/services/message/__init__.py
git mv app/services/chat/cache.py app/domains/chat/services/cache.py
git mv app/services/chat/__init__.py app/domains/chat/services/__init__.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

- [ ] **Step 3: Fix internal imports within moved chat domain files**

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move chat domain to app/domains/chat/"
```

---

### Task 7: Move the Loan domain

**Files:**
- Move: `app/models/loan.py` -> `app/domains/loan/models.py`
- Move: `app/errors/loan.py` -> `app/domains/loan/errors.py`
- Move: `app/schemas/loan/` -> `app/domains/loan/schemas/`
- Move: `app/services/loan/` -> `app/domains/loan/services/`

- [ ] **Step 1: Move files**

```bash
git mv app/models/loan.py app/domains/loan/models.py
git mv app/errors/loan.py app/domains/loan/errors.py

mkdir -p app/domains/loan/schemas
git mv app/schemas/loan/base.py app/domains/loan/schemas/base.py
git mv app/schemas/loan/read.py app/domains/loan/schemas/read.py
git mv app/schemas/loan/api.py app/domains/loan/schemas/api.py
git mv app/schemas/loan/query.py app/domains/loan/schemas/query.py

mkdir -p app/domains/loan/services/loan
mkdir -p app/domains/loan/services/request
git mv app/services/loan/loan/create.py app/domains/loan/services/loan/create.py
git mv app/services/loan/loan/read.py app/domains/loan/services/loan/read.py
git mv app/services/loan/loan/update.py app/domains/loan/services/loan/update.py
git mv app/services/loan/loan/__init__.py app/domains/loan/services/loan/__init__.py
git mv app/services/loan/request/create.py app/domains/loan/services/request/create.py
git mv app/services/loan/request/read.py app/domains/loan/services/request/read.py
git mv app/services/loan/request/update.py app/domains/loan/services/request/update.py
git mv app/services/loan/request/accept.py app/domains/loan/services/request/accept.py
git mv app/services/loan/request/reject.py app/domains/loan/services/request/reject.py
git mv app/services/loan/request/cancel.py app/domains/loan/services/request/cancel.py
git mv app/services/loan/request/__init__.py app/domains/loan/services/request/__init__.py
git mv app/services/loan/cache.py app/domains/loan/services/cache.py
git mv app/services/loan/__init__.py app/domains/loan/services/__init__.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

- [ ] **Step 3: Fix internal imports within moved loan domain files**

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move loan domain to app/domains/loan/"
```

---

### Task 8: Move the Auth domain

**Files:**
- Move: `app/models/auth.py` -> `app/domains/auth/models.py`
- Move: `app/errors/auth.py` -> `app/domains/auth/errors.py`
- Move: `app/schemas/auth/` -> `app/domains/auth/schemas/`
- Move: `app/services/auth/` -> `app/domains/auth/services/`
- Move: `app/clients/database/auth/` -> `app/domains/auth/db/` (auth-specific DB operations)

- [ ] **Step 1: Move files**

```bash
git mv app/models/auth.py app/domains/auth/models.py
git mv app/errors/auth.py app/domains/auth/errors.py

mkdir -p app/domains/auth/schemas
git mv app/schemas/auth/base.py app/domains/auth/schemas/base.py
git mv app/schemas/auth/create.py app/domains/auth/schemas/create.py
git mv app/schemas/auth/read.py app/domains/auth/schemas/read.py
git mv app/schemas/auth/form.py app/domains/auth/schemas/form.py
git mv app/schemas/auth/api.py app/domains/auth/schemas/api.py
git mv app/schemas/auth/query.py app/domains/auth/schemas/query.py
git mv app/schemas/auth/credentials.py app/domains/auth/schemas/credentials.py
git mv app/schemas/auth/data.py app/domains/auth/schemas/data.py
git mv app/schemas/auth/reset.py app/domains/auth/schemas/reset.py
git mv app/schemas/auth/validation.py app/domains/auth/schemas/validation.py
git mv app/schemas/auth/availability.py app/domains/auth/schemas/availability.py

mkdir -p app/domains/auth/services
git mv app/services/auth/access_token.py app/domains/auth/services/access_token.py
git mv app/services/auth/credentials.py app/domains/auth/services/credentials.py
git mv app/services/auth/password.py app/domains/auth/services/password.py
git mv app/services/auth/refresh_token.py app/domains/auth/services/refresh_token.py
git mv app/services/auth/reset.py app/domains/auth/services/reset.py
git mv app/services/auth/validation.py app/domains/auth/services/validation.py
git mv app/services/auth/__init__.py app/domains/auth/services/__init__.py

mkdir -p app/domains/auth/db
git mv app/clients/database/auth/create.py app/domains/auth/db/create.py
git mv app/clients/database/auth/read.py app/domains/auth/db/read.py
git mv app/clients/database/auth/update.py app/domains/auth/db/update.py
git mv app/clients/database/auth/delete.py app/domains/auth/db/delete.py
git mv app/clients/database/auth/__init__.py app/domains/auth/db/__init__.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

- [ ] **Step 3: Fix internal imports within moved auth domain files**

Key: auth services import from `app.clients.database.auth.*` — update to `app.domains.auth.db.*`.

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move auth domain to app/domains/auth/"
```

---

### Task 9: Move the Image domain

**Files:**
- Move: `app/errors/image.py` -> `app/domains/image/errors.py`
- Move: `app/schemas/image/` -> `app/domains/image/schemas/`
- Move: `app/services/image/` -> `app/domains/image/services/`
- Move: `app/clients/database/image/` -> `app/domains/image/db/`

- [ ] **Step 1: Move files**

```bash
git mv app/errors/image.py app/domains/image/errors.py

mkdir -p app/domains/image/schemas
git mv app/schemas/image/base.py app/domains/image/schemas/base.py
git mv app/schemas/image/read.py app/domains/image/schemas/read.py

mkdir -p app/domains/image/services
git mv app/services/image/create.py app/domains/image/services/create.py
git mv app/services/image/read.py app/domains/image/services/read.py
git mv app/services/image/constants.py app/domains/image/services/constants.py
git mv app/services/image/__init__.py app/domains/image/services/__init__.py

mkdir -p app/domains/image/db
git mv app/clients/database/image/create.py app/domains/image/db/create.py
git mv app/clients/database/image/read.py app/domains/image/db/read.py
git mv app/clients/database/image/__init__.py app/domains/image/db/__init__.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

- [ ] **Step 3: Fix internal imports**

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move image domain to app/domains/image/"
```

---

### Task 10: Move the Region domain

**Files:**
- Move: `app/errors/region.py` -> `app/domains/region/errors.py`
- Move: `app/schemas/region/` -> `app/domains/region/schemas/`
- Move: `app/services/region/` -> `app/domains/region/services/`

- [ ] **Step 1: Move files**

```bash
git mv app/errors/region.py app/domains/region/errors.py

mkdir -p app/domains/region/schemas
git mv app/schemas/region/base.py app/domains/region/schemas/base.py
git mv app/schemas/region/create.py app/domains/region/schemas/create.py
git mv app/schemas/region/read.py app/domains/region/schemas/read.py
git mv app/schemas/region/update.py app/domains/region/schemas/update.py

mkdir -p app/domains/region/services
git mv app/services/region/create.py app/domains/region/services/create.py
git mv app/services/region/read.py app/domains/region/services/read.py
git mv app/services/region/__init__.py app/domains/region/services/__init__.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

- [ ] **Step 3: Fix internal imports**

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move region domain to app/domains/region/"
```

---

### Task 11: Move the Category domain

**Files:**
- Move: `app/errors/category.py` -> `app/domains/category/errors.py`
- Move: `app/schemas/category/` -> `app/domains/category/schemas/`
- Move: `app/services/category/` -> `app/domains/category/services/`

- [ ] **Step 1: Move files**

```bash
git mv app/errors/category.py app/domains/category/errors.py

mkdir -p app/domains/category/schemas
git mv app/schemas/category/base.py app/domains/category/schemas/base.py
git mv app/schemas/category/create.py app/domains/category/schemas/create.py
git mv app/schemas/category/read.py app/domains/category/schemas/read.py
git mv app/schemas/category/__init__.py app/domains/category/schemas/__init__.py

mkdir -p app/domains/category/services
git mv app/services/category/create.py app/domains/category/services/create.py
git mv app/services/category/read.py app/domains/category/services/read.py
git mv app/services/category/__init__.py app/domains/category/services/__init__.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

- [ ] **Step 3: Fix internal imports**

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move category domain to app/domains/category/"
```

---

### Task 12: Move the Report domain

**Files:**
- Move: `app/models/report.py` -> `app/domains/report/models.py`
- Move: `app/schemas/report/` -> `app/domains/report/schemas/`

- [ ] **Step 1: Move files**

```bash
git mv app/models/report.py app/domains/report/models.py

mkdir -p app/domains/report/schemas
git mv app/schemas/report/base.py app/domains/report/schemas/base.py
git mv app/schemas/report/create.py app/domains/report/schemas/create.py
```

- [ ] **Step 2: Create compatibility re-exports at old locations**

- [ ] **Step 3: Fix internal imports**

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move report domain to app/domains/report/"
```

---

### Task 13: Move enums into domains

**Files:**
- Modify: `app/enums.py` — split contents into domain-specific locations
- Create: `app/domains/chat/enums.py` (ChatMessageType)
- Create: `app/domains/loan/enums.py` (LoanRequestState)
- Create: `app/domains/report/enums.py` (ReportType)
- Create: `app/domains/item/enums.py` (ItemQueryAvailability)
- Keep: `app/enums.py` as re-export shim (EnumWithMetadata base stays or moves to `app/shared/enums.py`)

- [ ] **Step 1: Read current enums.py to identify all enums and their domains**

- [ ] **Step 2: Create domain-specific enum files**

Move each enum class to its domain. If there's a shared base class (`EnumWithMetadata`), move it to `app/shared/enums.py`.

- [ ] **Step 3: Create re-export shim at `app/enums.py`**

```python
# app/enums.py — compatibility re-export
from app.shared.enums import EnumWithMetadata  # noqa: F401
from app.domains.chat.enums import ChatMessageType  # noqa: F401
from app.domains.loan.enums import LoanRequestState  # noqa: F401
from app.domains.report.enums import ReportType  # noqa: F401
from app.domains.item.enums import ItemQueryAvailability  # noqa: F401
```

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: split enums into domain-specific files"
```

---

## Phase 3: Update Alembic and App Entry Points

### Task 14: Update Alembic configuration

**Files:**
- Modify: `alembic/env.py`
- Modify: `app/models/__init__.py` (ensure it still exports `Base` for Alembic)

- [ ] **Step 1: Update alembic/env.py**

Currently `alembic/env.py` does:
```python
import app
target_metadata = app.models.Base.metadata
```

And:
```python
db_config = app.config.DatabaseConfig.from_env()
```

Update to:
```python
import app.domains  # noqa: F401 — triggers model registration
from app.shared.models import Base
from app.infrastructure.config import DatabaseConfig

target_metadata = Base.metadata

if config.get_main_option("sqlalchemy.url") is None:
    db_config = DatabaseConfig.from_env()
    config.set_main_option(
        "sqlalchemy.url", db_config.url.render_as_string(hide_password=False)
    )
```

- [ ] **Step 2: Ensure all domain models are imported**

`app/domains/__init__.py` must import all domain model modules so they register with SQLAlchemy's metadata:

```python
# app/domains/__init__.py
from app.domains.item import models as _item_models  # noqa: F401
from app.domains.user import models as _user_models  # noqa: F401
from app.domains.chat import models as _chat_models  # noqa: F401
from app.domains.loan import models as _loan_models  # noqa: F401
from app.domains.auth import models as _auth_models  # noqa: F401
from app.domains.report import models as _report_models  # noqa: F401
```

- [ ] **Step 3: Verify Alembic can see all models**

```bash
alembic check
```

This should report "No new upgrade operations detected" if no model changes were made.

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: update alembic to use new domain model locations"
```

---

### Task 15: Update app.py and main.py

**Files:**
- Modify: `app/app.py`
- Modify: `app/main.py`

- [ ] **Step 1: Update app.py imports**

Replace all old-path imports with new infrastructure/domain paths:

```python
# Before
from .config import Config
from .database import create_session_maker, init_db_session_dependency
from .email import init_email_dependency
from .pubsub import init_broadcast_dependency
from .cache import init_cache_dependency
from .clients.cache import Cache
from .clients.redis import create_redis_client

# After
from .infrastructure.config import Config
from .infrastructure.database import create_session_maker, init_db_session_dependency
from .infrastructure.email import init_email_dependency
from .infrastructure.pubsub import init_broadcast_dependency
from .infrastructure.cache import init_cache_dependency
from .infrastructure.cache_client import Cache
from .infrastructure.redis import create_redis_client
```

Also ensure `app/domains/__init__.py` is imported so models register (can add `import app.domains` at top).

- [ ] **Step 2: Update main.py imports**

```python
# Before
from .app import create_app
from .config import Config

# After
from .app import create_app
from .infrastructure.config import Config
```

- [ ] **Step 3: Run tests**

```bash
mise run test
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: update app.py and main.py to use new import paths"
```

---

## Phase 4: Rewrite All Consumer Imports

### Task 16: Update all router imports to use domain paths

**Files:**
- Modify: all files under `app/routers/v1/` (~47 files with old imports)

- [ ] **Step 1: Global search-and-replace for router imports**

Use the following replacements across all files in `app/routers/`:

| Old import | New import |
|---|---|
| `from app import services` | `from app import domains` (then `domains.item.services.*`, etc.) |
| `from app.schemas.item.` | `from app.domains.item.schemas.` |
| `from app.schemas.chat.` | `from app.domains.chat.schemas.` |
| `from app.schemas.loan.` | `from app.domains.loan.schemas.` |
| `from app.schemas.user.` | `from app.domains.user.schemas.` |
| `from app.schemas.auth.` | `from app.domains.auth.schemas.` |
| `from app.schemas.image.` | `from app.domains.image.schemas.` |
| `from app.schemas.region.` | `from app.domains.region.schemas.` |
| `from app.schemas.report.` | `from app.domains.report.schemas.` |
| `from app.schemas.category.` | `from app.domains.category.schemas.` |
| `from app.schemas.pubsub` | `from app.domains.chat.schemas.pubsub` |
| `from app.schemas.websocket` | `from app.domains.chat.schemas.websocket` |
| `from app.schemas.query` | `from app.shared.pagination` |
| `from app.schemas.utils` | `from app.shared.utils` |
| `from app.schemas.base` | `from app.shared.schemas` |
| `from app.errors` (base errors) | `from app.domains.*.errors` (per domain) or keep `from app.errors` for base classes |
| `from app.database` | `from app.infrastructure.database` |
| `from app.config` | `from app.infrastructure.config` |
| `from app.pubsub` | `from app.infrastructure.pubsub` |
| `from app.cache` | `from app.infrastructure.cache` |
| `from app.cache_keys` | `from app.infrastructure.cache_keys` |
| `from app.enums` | `from app.domains.{domain}.enums` (per usage) |

Also update `from app import services` pattern. Routers that do `services.item.list_items(...)` need to change to `from app.domains.item.services import list_items` or similar.

- [ ] **Step 2: Run lint to catch any missed imports**

```bash
mise run lint:ruff
```

Fix any import errors.

- [ ] **Step 3: Run tests**

```bash
mise run test
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: update all router imports to use domain paths"
```

---

### Task 17: Update all test imports to use domain paths

**Files:**
- Modify: all files under `tests/` (~53 files)

- [ ] **Step 1: Update fixture imports**

Fixtures in `tests/fixtures/` import from schemas, models, and enums. Apply the same replacement table from Task 16.

- [ ] **Step 2: Update test file imports**

Tests in `tests/item/`, `tests/chat/`, `tests/loan/`, `tests/user/`, and top-level test files. Same replacements.

- [ ] **Step 3: Update seed imports (if seed/ imports from app)**

Check `seed/` files for imports from old paths and update them.

- [ ] **Step 4: Run tests**

```bash
mise run test
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: update all test and seed imports to use domain paths"
```

---

### Task 18: Update cross-domain service imports

**Files:**
- Modify: all files under `app/domains/*/services/` that import from other domains

- [ ] **Step 1: Find all cross-domain imports that still use old paths**

```bash
grep -rn "from app\.services\." app/domains/
grep -rn "from app\.models\." app/domains/
grep -rn "from app\.schemas\." app/domains/
grep -rn "from app\.errors\." app/domains/
grep -rn "from app\.clients\." app/domains/
```

- [ ] **Step 2: Replace each with the new domain path**

Examples:
- `from app.services.user.star.update import add_many_stars` -> `from app.domains.user.services.star.update import add_many_stars`
- `from app.services.image.read import check_image_owners` -> `from app.domains.image.services.read import check_image_owners`
- `from app.models.item.item import Item` -> `from app.domains.item.models.item import Item`

- [ ] **Step 3: Run tests**

```bash
mise run test
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: update all cross-domain imports to use domain paths"
```

---

## Phase 5: Remove Compatibility Shims

### Task 19: Delete old directories and re-export shims

**Files:**
- Delete: `app/models/` (all files are now re-exports)
- Delete: `app/schemas/` (all files are now re-exports)
- Delete: `app/services/` (all files are now re-exports)
- Delete: `app/errors/` (keep `app/errors/__init__.py` and `app/errors/base.py` if base error classes aren't domain-specific, or move to `app/shared/errors.py`)
- Delete: `app/clients/` (all absorbed)
- Delete: `app/domain/` (star.py moved to user domain)
- Delete: `app/utils/` (moved to shared)
- Delete: shim files at `app/config.py`, `app/database.py`, `app/pubsub.py`, `app/email.py`, `app/cache.py`, `app/cache_keys.py`, `app/enums.py`

- [ ] **Step 1: Verify no remaining imports reference old paths**

```bash
grep -rn "from app\.models\." app/ tests/ seed/ alembic/ --include="*.py" | grep -v "^Binary" | grep -v "__pycache__"
grep -rn "from app\.schemas\." app/ tests/ seed/ alembic/ --include="*.py" | grep -v "__pycache__"
grep -rn "from app\.services\." app/ tests/ seed/ alembic/ --include="*.py" | grep -v "__pycache__"
grep -rn "from app\.clients\." app/ tests/ seed/ alembic/ --include="*.py" | grep -v "__pycache__"
grep -rn "from app\.errors\." app/ tests/ seed/ alembic/ --include="*.py" | grep -v "__pycache__"
grep -rn "from app\.domain\." app/ tests/ seed/ alembic/ --include="*.py" | grep -v "__pycache__"
grep -rn "from app\.utils\." app/ tests/ seed/ alembic/ --include="*.py" | grep -v "__pycache__"
grep -rn "from app\.config" app/ tests/ seed/ alembic/ --include="*.py" | grep -v "infrastructure" | grep -v "__pycache__"
grep -rn "from app\.database" app/ tests/ seed/ alembic/ --include="*.py" | grep -v "infrastructure" | grep -v "__pycache__"
grep -rn "from app\.pubsub" app/ tests/ seed/ alembic/ --include="*.py" | grep -v "infrastructure" | grep -v "__pycache__"
grep -rn "from app\.email" app/ tests/ seed/ alembic/ --include="*.py" | grep -v "infrastructure" | grep -v "__pycache__"
grep -rn "from app\.cache" app/ tests/ seed/ alembic/ --include="*.py" | grep -v "infrastructure" | grep -v "__pycache__"
grep -rn "from app\.enums" app/ tests/ seed/ alembic/ --include="*.py" | grep -v "domains" | grep -v "__pycache__"
grep -rn "from app import services" app/ tests/ --include="*.py" | grep -v "__pycache__"
```

If any matches remain, fix them before proceeding.

- [ ] **Step 2: Move base errors to shared**

```bash
git mv app/errors/base.py app/shared/errors.py
```

Update `app/app.py` to import `ApiError` from `app.shared.errors`.

Update any domain error files that inherit from `ApiError`:
```python
# Before
from app.errors.base import ApiError, NotFoundError, ...

# After
from app.shared.errors import ApiError, NotFoundError, ...
```

- [ ] **Step 3: Delete old directories**

```bash
rm -rf app/models/
rm -rf app/schemas/
rm -rf app/services/
rm -rf app/errors/
rm -rf app/clients/
rm -rf app/domain/
rm -rf app/utils/
rm -f app/config.py app/database.py app/pubsub.py app/email.py app/cache.py app/cache_keys.py app/enums.py
```

- [ ] **Step 4: Run lint**

```bash
mise run lint
```

Fix any issues (unused imports, missing imports).

- [ ] **Step 5: Run tests**

```bash
mise run test
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor: remove old directories and compatibility shims"
```

---

## Phase 6: Extract Composable Filters

### Task 20: Create shared filter helpers

**Files:**
- Create: `app/shared/filters.py`

- [ ] **Step 1: Read existing pagination utilities**

Read `app/shared/pagination.py` (was `app/schemas/query.py`) and `app/shared/pagination_utils.py` (was `app/utils/pagination.py`) to understand current pagination patterns.

- [ ] **Step 2: Write shared filter helpers**

```python
# app/shared/filters.py

from sqlalchemy import Select, func, text


def order_by_newest(stmt: Select) -> Select:
    """Order by id descending (newest first)."""
    return stmt.order_by(text("id DESC"))


def paginate_by_id(stmt: Select, *, cursor: int | None = None, limit: int = 32) -> Select:
    """Cursor-based keyset pagination using id.

    Fetches limit+1 rows to detect whether a next page exists.
    """
    if cursor is not None:
        stmt = stmt.where(text("id < :cursor")).params(cursor=cursor)
    return stmt.limit(limit + 1)
```

- [ ] **Step 3: Run tests (nothing uses this yet, just verify no syntax errors)**

```bash
python -c "from app.shared.filters import order_by_newest, paginate_by_id"
```

- [ ] **Step 4: Commit**

```bash
git add app/shared/filters.py
git commit -m "refactor: add shared composable filter helpers"
```

---

### Task 21: Extract Item domain filters

This is the most complex domain. The goal is to extract filter logic from `app/domains/item/services/read/list.py` (350+ LOC), `app/domains/item/services/read/selections.py`, and `app/domains/item/services/read/user_sets.py` into composable `Select -> Select` functions.

**Files:**
- Create: `app/domains/item/filters.py`
- Modify: `app/domains/item/services/read/list.py`
- Modify: `app/domains/item/services/read/selections.py` (may be absorbed into filters)
- Modify: `app/domains/item/services/read/user_sets.py` (may be absorbed into filters)

- [ ] **Step 1: Read the current service files to identify extractable filter logic**

Read these files:
- `app/domains/item/services/read/list.py`
- `app/domains/item/services/read/selections.py`
- `app/domains/item/services/read/user_sets.py`
- `app/domains/item/services/read/get.py`

Identify every `where()`, `join()`, subquery, and ordering clause. Each becomes a candidate filter function.

- [ ] **Step 2: Create filters.py with all extracted filter functions**

Based on what exists in the service files, create functions like:

```python
# app/domains/item/filters.py

from sqlalchemy import Select, func, literal, select, and_
from app.domains.item.models.item import Item
from app.domains.item.models.like import ItemLike
from app.domains.item.models.save import ItemSave


def available(stmt: Select) -> Select:
    """Only items where available == True."""
    return stmt.where(Item.available == True)  # noqa: E712


def not_available(stmt: Select) -> Select:
    return stmt.where(Item.available == False)  # noqa: E712


def owned_by(stmt: Select, user_id: int) -> Select:
    return stmt.where(Item.owner_id == user_id)


def not_owned_by(stmt: Select, user_id: int) -> Select:
    return stmt.where(Item.owner_id != user_id)


def matching_words(stmt: Select, words: str) -> Select:
    """Trigram similarity search. Adds words_match column, filters, orders."""
    # Adapt from the existing searchable_text logic in list.py
    match_pct = func.similarity(Item.searchable_text, func.normalize_text(words))
    return (
        stmt
        .add_columns(match_pct.label("words_match"))
        .where(match_pct > 0.1)
        .order_by(match_pct.desc())
    )


def in_regions(stmt: Select, region_ids: list[int]) -> Select:
    """Filter to items in any of the given regions."""
    # Adapt from existing region filter logic
    ...


def in_categories(stmt: Select, category_ids: list[int]) -> Select:
    """Filter to items in any of the given categories."""
    ...


def with_liked_flag(stmt: Select, user_id: int) -> Select:
    """Add 'liked' boolean column for the given viewer."""
    liked_subq = (
        select(literal(True))
        .where(and_(ItemLike.item_id == Item.id, ItemLike.user_id == user_id))
        .correlate(Item)
        .exists()
    )
    return stmt.add_columns(liked_subq.label("liked"))


def with_saved_flag(stmt: Select, user_id: int) -> Select:
    """Add 'saved' boolean column for the given viewer."""
    saved_subq = (
        select(literal(True))
        .where(and_(ItemSave.item_id == Item.id, ItemSave.user_id == user_id))
        .correlate(Item)
        .exists()
    )
    return stmt.add_columns(saved_subq.label("saved"))


def with_owned_flag(stmt: Select, user_id: int) -> Select:
    """Add 'owned' boolean column for the given viewer."""
    return stmt.add_columns((Item.owner_id == user_id).label("owned"))
```

The exact implementation of each function must be adapted from the existing code in `selections.py`, `user_sets.py`, and `list.py`. Read those files and translate each query fragment into a standalone filter function.

- [ ] **Step 3: Refactor list_items to use filter composition**

Replace the monolithic query building in `list.py` with filter composition:

```python
# app/domains/item/services/read/list.py (simplified)

from app.domains.item import filters as f
from app.shared.filters import paginate_by_id, order_by_newest

async def list_items(db: AsyncSession, ...) -> ...:
    stmt = select(Item)

    # Apply filters based on query params
    if words:
        stmt = f.matching_words(stmt, words)
    else:
        stmt = order_by_newest(stmt)

    if query_filter:
        if query_filter.available == ItemQueryAvailability.YES:
            stmt = f.available(stmt)
        elif query_filter.available == ItemQueryAvailability.NO:
            stmt = f.not_available(stmt)
        if query_filter.region_ids:
            stmt = f.in_regions(stmt, query_filter.region_ids)
        if query_filter.category_ids:
            stmt = f.in_categories(stmt, query_filter.category_ids)

    # Viewer-dependent columns
    if client_id:
        stmt = f.with_liked_flag(stmt, client_id)
        stmt = f.with_saved_flag(stmt, client_id)
        stmt = f.with_owned_flag(stmt, client_id)

    # Pagination
    stmt = paginate_by_id(stmt, cursor=page_options.cursor, limit=page_options.limit)

    result = await db.execute(stmt)
    ...
```

- [ ] **Step 4: Run the item tests**

```bash
pytest tests/item/ -v
```

- [ ] **Step 5: Run the full test suite**

```bash
mise run test
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor: extract item domain composable query filters"
```

---

### Task 22: Extract Chat domain filters

**Files:**
- Create: `app/domains/chat/filters.py`
- Modify: `app/domains/chat/services/chat/read.py`
- Modify: `app/domains/chat/services/message/read.py`

- [ ] **Step 1: Read chat service read files to identify filter candidates**

- [ ] **Step 2: Create chat filters**

```python
# app/domains/chat/filters.py

from sqlalchemy import Select
from app.domains.chat.models import Chat, ChatMessage


def for_member(stmt: Select, user_id: int) -> Select:
    """Chats where user is owner or borrower."""
    return stmt.where(
        (Chat.owner_id == user_id) | (Chat.borrower_id == user_id)
    )


def for_item(stmt: Select, item_id: int) -> Select:
    return stmt.where(Chat.item_id == item_id)


def messages_for_chat(stmt: Select, item_id: int, borrower_id: int) -> Select:
    return stmt.where(
        (ChatMessage.item_id == item_id) & (ChatMessage.borrower_id == borrower_id)
    )
```

Adapt from existing chat read logic.

- [ ] **Step 3: Refactor chat read services to use filters**

- [ ] **Step 4: Run chat tests**

```bash
pytest tests/chat/ -v
```

- [ ] **Step 5: Run full test suite**

```bash
mise run test
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor: extract chat domain composable query filters"
```

---

### Task 23: Extract Loan domain filters

**Files:**
- Create: `app/domains/loan/filters.py`
- Modify: `app/domains/loan/services/loan/read.py`
- Modify: `app/domains/loan/services/request/read.py`

- [ ] **Step 1: Read loan service read files**

- [ ] **Step 2: Create loan filters**

```python
# app/domains/loan/filters.py

from sqlalchemy import Select
from app.domains.loan.models import Loan, LoanRequest


def requests_for_item(stmt: Select, item_id: int) -> Select:
    return stmt.where(LoanRequest.item_id == item_id)


def requests_for_borrower(stmt: Select, borrower_id: int) -> Select:
    return stmt.where(LoanRequest.borrower_id == borrower_id)


def requests_in_states(stmt: Select, states: list) -> Select:
    return stmt.where(LoanRequest.state.in_(states))


def loans_for_item(stmt: Select, item_id: int) -> Select:
    return stmt.where(Loan.item_id == item_id)


def active_loans(stmt: Select) -> Select:
    """Loans where 'during' range includes now."""
    from sqlalchemy import func
    return stmt.where(Loan.during.contains(func.now()))
```

Adapt from existing loan read logic.

- [ ] **Step 3: Refactor loan read services to use filters**

- [ ] **Step 4: Run loan tests**

```bash
pytest tests/loan/ -v
```

- [ ] **Step 5: Run full test suite**

```bash
mise run test
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor: extract loan domain composable query filters"
```

---

### Task 24: Extract User domain filters

**Files:**
- Create: `app/domains/user/filters.py`
- Modify: `app/domains/user/services/read.py`

- [ ] **Step 1: Read user service read file**

- [ ] **Step 2: Create user filters**

```python
# app/domains/user/filters.py

from sqlalchemy import Select
from app.domains.user.models import User


def by_email(stmt: Select, email: str) -> Select:
    return stmt.where(User.email == email)


def by_name(stmt: Select, name: str) -> Select:
    return stmt.where(User.name == name)


def validated(stmt: Select) -> Select:
    return stmt.where(User.validation_code.is_(None))
```

- [ ] **Step 3: Refactor user read service to use filters where it simplifies**

- [ ] **Step 4: Run user tests**

```bash
pytest tests/user/ -v
```

- [ ] **Step 5: Run full test suite**

```bash
mise run test
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor: extract user domain composable query filters"
```

---

## Phase 7: Final Cleanup

### Task 25: Run full lint and fix

**Files:**
- Modify: any files with lint violations

- [ ] **Step 1: Run ruff**

```bash
mise run lint:ruff
```

Fix all issues. Common: unused imports from removed re-exports, import ordering.

- [ ] **Step 2: Run mypy**

```bash
mise run lint:mypy
```

Fix type errors from moved modules.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor: fix lint and type errors after restructure"
```

---

### Task 26: Run full test suite and fix any remaining issues

- [ ] **Step 1: Run full test suite**

```bash
mise run test
```

- [ ] **Step 2: If failures, investigate and fix**

Common issues:
- Fixture imports still using old paths
- Alembic model discovery missing a domain
- Cache key imports pointing to old location
- Seed files with stale imports

- [ ] **Step 3: Commit fixes**

```bash
git add -A
git commit -m "fix: resolve remaining test failures after restructure"
```

---

### Task 27: Update domain `__init__.py` public APIs

**Files:**
- Modify: `app/domains/{each}/__init__.py`

- [ ] **Step 1: Define public API for each domain**

Each domain's `__init__.py` should export the key symbols that other domains and routers need:

```python
# app/domains/item/__init__.py
from app.domains.item.models.item import Item
from app.domains.item.errors import ItemNotFoundError
# services are imported directly: from app.domains.item.services import ...
```

Only export what's actually used cross-domain. This documents the boundary.

- [ ] **Step 2: Run tests**

```bash
mise run test
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor: define domain public API exports"
```

---

### Task 28: Verify cross-domain dependency rules

- [ ] **Step 1: Check for dependency direction violations**

Allowed directions (from spec):
```
item   -> user, image, region, category
chat   -> item, loan, user
loan   -> item
auth   -> user
report -> user, item, chat
```

```bash
# Check for reverse dependencies (violations)
grep -rn "from app\.domains\.item\." app/domains/user/ app/domains/auth/ app/domains/loan/
grep -rn "from app\.domains\.chat\." app/domains/item/ app/domains/user/ app/domains/auth/
grep -rn "from app\.domains\.loan\." app/domains/item/ app/domains/user/ app/domains/auth/
```

Any matches are violations — fix by extracting shared logic to `app/shared/` or restructuring the call.

- [ ] **Step 2: Commit any fixes**

```bash
git add -A
git commit -m "refactor: fix cross-domain dependency violations"
```

---

### Task 29: Final verification

- [ ] **Step 1: Run full lint**

```bash
mise run lint
```

- [ ] **Step 2: Run full test suite**

```bash
mise run test
```

- [ ] **Step 3: Verify directory structure matches spec**

```bash
find app/domains -type f -name "*.py" | sort
find app/infrastructure -type f -name "*.py" | sort
find app/shared -type f -name "*.py" | sort
# Verify no leftover files in old locations
ls app/models/ 2>/dev/null && echo "WARN: app/models/ still exists"
ls app/schemas/ 2>/dev/null && echo "WARN: app/schemas/ still exists"
ls app/services/ 2>/dev/null && echo "WARN: app/services/ still exists"
ls app/clients/ 2>/dev/null && echo "WARN: app/clients/ still exists"
ls app/errors/ 2>/dev/null && echo "WARN: app/errors/ still exists"
```

- [ ] **Step 4: Verify Alembic**

```bash
alembic check
```

- [ ] **Step 5: Final commit if any cleanup needed**

```bash
git add -A
git commit -m "refactor: final cleanup of DDD-lite restructure"
```

---

## Summary

| Phase | Tasks | Description |
|---|---|---|
| 1 | 1-3 | Scaffold directories, move infrastructure & shared utilities |
| 2 | 4-13 | Move each domain (item, user, chat, loan, auth, image, region, category, report, enums) |
| 3 | 14-15 | Update Alembic and app entry points |
| 4 | 16-18 | Rewrite all consumer imports (routers, tests, cross-domain) |
| 5 | 19 | Remove compatibility shims and old directories |
| 6 | 20-24 | Extract composable filters per domain |
| 7 | 25-29 | Lint, test, public APIs, dependency rules, final verification |

Total: 29 tasks. Tests run after every task to catch breakage early.
