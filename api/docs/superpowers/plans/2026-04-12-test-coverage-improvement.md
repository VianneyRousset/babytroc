# Test Coverage Improvement & Report Features — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fill test gaps for stars/saved/liked/borrowings, implement the report system (user/item/chat) with evidence snapshots, add edge case tests for pagination/auth/inputs, and add targeted WebSocket tests.

**Architecture:** Phase 1 tests existing untested code (and fixes bugs found). Phase 2 implements report services that snapshot entity state into a `saved_info` JSON column and send moderator emails, then tests them. Phase 3 adds robustness/edge-case tests. Phase 4 adds WebSocket-specific tests.

**Tech Stack:** FastAPI, SQLAlchemy async, pytest-asyncio, httpx, httpx-ws, PyJWT, fastapi-mail

---

## File Structure

### New files
| File | Responsibility |
|------|---------------|
| `tests/user/test_user_stars.py` | Stars service + domain tests |
| `tests/item/test_item_save.py` | Saved items CRUD tests |
| `tests/item/test_item_like_operations.py` | Like/unlike + counts tests |
| `tests/test_report.py` | Report user/item/chat tests |
| `tests/test_pagination_edge_cases.py` | Pagination boundary tests |
| `tests/test_edge_cases.py` | Malformed input tests |
| `tests/test_websocket.py` | WebSocket auth, relay, isolation tests |
| `app/services/item/report.py` | Item report service |
| `app/clients/email/report.py` | Moderator report email sender |

### Modified files
| File | Change |
|------|--------|
| `app/services/user/report.py` | Fill stub with snapshot + DB insert + email |
| `app/services/chat/chat/report.py` | Fill stub with snapshot + DB insert + email |
| `app/routers/v1/items/report.py` | Replace `NotImplementedError` with service call |
| `app/services/item/__init__.py` | Export `report_item` |
| `app/clients/email/__init__.py` | Export `send_report_email` |
| `app/routers/v1/me/borrowings/read.py` | Fix `owner_id` → `borrower_id` bug |
| `tests/loan/test_loans_read.py` | Add borrowing endpoint tests |
| `tests/test_auth.py` | Add token edge case tests |

---

## Task 1: Stars service tests

**Files:**
- Create: `tests/user/test_user_stars.py`
- Reference: `app/services/user/star/update.py`, `app/domain/star.py`

- [ ] **Step 1: Write stars tests**

```python
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.domain.star import stars_gain_when_adding_item
from app.errors.user import UserNotFoundError
from app.services.user import get_user
from app.services.user.star.update import (
    AddUserStars,
    add_many_stars_to_users,
    add_stars_to_user,
)
from app.schemas.user.private import UserPrivateRead


class TestStarsDomain:
    """Test stars domain function."""

    def test_stars_gain_when_adding_item(self):
        assert stars_gain_when_adding_item(1) == 20
        assert stars_gain_when_adding_item(3) == 60
        assert stars_gain_when_adding_item(0) == 0

    def test_stars_gain_invalid_input(self):
        with pytest.raises(ValueError, match="must be an integer"):
            stars_gain_when_adding_item("not_an_int")  # type: ignore[arg-type]


class TestStarsService:
    """Test stars service."""

    async def test_add_stars_to_user(
        self,
        database_sessionmaker: async_sessionmaker,
        alice: UserPrivateRead,
    ):
        async with database_sessionmaker.begin() as session:
            user_before = await get_user(db=session, user_id=alice.id)
            old_count = user_before.stars_count

        async with database_sessionmaker.begin() as session:
            await add_stars_to_user(db=session, user_id=alice.id, count=10)

        async with database_sessionmaker.begin() as session:
            user_after = await get_user(db=session, user_id=alice.id)
            assert user_after.stars_count == old_count + 10

    async def test_add_many_stars_to_users(
        self,
        database_sessionmaker: async_sessionmaker,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
    ):
        async with database_sessionmaker.begin() as session:
            alice_before = await get_user(db=session, user_id=alice.id)
            bob_before = await get_user(db=session, user_id=bob.id)

        async with database_sessionmaker.begin() as session:
            await add_many_stars_to_users(
                db=session,
                stars=[
                    AddUserStars(user_id=alice.id, stars_count=5),
                    AddUserStars(user_id=bob.id, stars_count=15),
                ],
            )

        async with database_sessionmaker.begin() as session:
            alice_after = await get_user(db=session, user_id=alice.id)
            bob_after = await get_user(db=session, user_id=bob.id)
            assert alice_after.stars_count == alice_before.stars_count + 5
            assert bob_after.stars_count == bob_before.stars_count + 15

    async def test_add_stars_duplicate_user_raises(
        self,
        database_sessionmaker: async_sessionmaker,
        alice: UserPrivateRead,
    ):
        async with database_sessionmaker.begin() as session:
            with pytest.raises(ValueError, match="Non-unique user"):
                await add_many_stars_to_users(
                    db=session,
                    stars=[
                        AddUserStars(user_id=alice.id, stars_count=5),
                        AddUserStars(user_id=alice.id, stars_count=10),
                    ],
                )

    async def test_add_stars_non_existent_user_raises(
        self,
        database_sessionmaker: async_sessionmaker,
    ):
        async with database_sessionmaker.begin() as session:
            with pytest.raises(UserNotFoundError):
                await add_stars_to_user(db=session, user_id=999999, count=10)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/user/test_user_stars.py -v`
Expected: All 6 tests PASS (these test existing working code).

- [ ] **Step 3: Commit**

```bash
git add tests/user/test_user_stars.py
git commit -m "test: add stars service and domain tests"
```

---

## Task 2: Saved items tests

**Files:**
- Create: `tests/item/test_item_save.py`
- Reference: `app/routers/v1/me/saved.py`

- [ ] **Step 1: Write saved items tests**

```python
import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead


@pytest.mark.usefixtures("items")
class TestItemSave:
    """Test saved items CRUD."""

    async def test_save_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Save an item and verify it appears in saved list."""
        item = bob_items[0]

        resp = await alice_client.post(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.get("/api/v1/me/saved")
        resp.raise_for_status()
        saved_ids = [i["id"] for i in resp.json()]
        assert item.id in saved_ids

    async def test_unsave_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Save then unsave an item, verify it disappears."""
        item = bob_items[0]

        resp = await alice_client.post(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.delete(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.get("/api/v1/me/saved")
        resp.raise_for_status()
        saved_ids = [i["id"] for i in resp.json()]
        assert item.id not in saved_ids

    async def test_get_saved_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Verify GET /me/saved/{item_id} returns the saved item."""
        item = bob_items[0]

        resp = await alice_client.post(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.get(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()
        assert resp.json()["id"] == item.id

    async def test_save_non_existent_item(
        self,
        alice_client: AsyncClient,
    ):
        """Saving a non-existent item should return 404."""
        resp = await alice_client.post("/api/v1/me/saved/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_unsave_non_saved_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Unsaving an item that was not saved should return 404."""
        item = bob_items[-1]
        resp = await alice_client.delete(f"/api/v1/me/saved/{item.id}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_save_item_twice(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Saving the same item twice should be idempotent or return error."""
        item = bob_items[0]

        resp = await alice_client.post(f"/api/v1/me/saved/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.post(f"/api/v1/me/saved/{item.id}")
        # either 200 (idempotent) or 409 (conflict) — both acceptable
        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_409_CONFLICT,
        )
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/item/test_item_save.py -v`
Expected: All 6 tests PASS. If any fail, the failure reveals a bug in the save service.

- [ ] **Step 3: Commit**

```bash
git add tests/item/test_item_save.py
git commit -m "test: add saved items CRUD tests"
```

---

## Task 3: Liked items operation tests

**Files:**
- Create: `tests/item/test_item_like_operations.py`
- Reference: `app/routers/v1/me/liked.py`

- [ ] **Step 1: Write like operations tests**

```python
import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead


@pytest.mark.usefixtures("items")
class TestItemLikeOperations:
    """Test like/unlike operations and counts."""

    async def test_like_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Like an item, verify it appears in liked list and likes_count increments."""
        item = bob_items[0]

        # get initial likes count
        resp = await alice_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        initial_likes = resp.json()["likes_count"]

        # like it
        resp = await alice_client.post(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        # verify in liked list
        resp = await alice_client.get("/api/v1/me/liked")
        resp.raise_for_status()
        liked_ids = [i["id"] for i in resp.json()]
        assert item.id in liked_ids

        # verify likes_count incremented
        resp = await alice_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        assert resp.json()["likes_count"] == initial_likes + 1

    async def test_unlike_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Like then unlike, verify removed and count decrements."""
        item = bob_items[0]

        # like
        resp = await alice_client.post(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        # get count after like
        resp = await alice_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        count_after_like = resp.json()["likes_count"]

        # unlike
        resp = await alice_client.delete(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        # verify removed from list
        resp = await alice_client.get("/api/v1/me/liked")
        resp.raise_for_status()
        liked_ids = [i["id"] for i in resp.json()]
        assert item.id not in liked_ids

        # verify count decremented
        resp = await alice_client.get(f"/api/v1/items/{item.id}")
        resp.raise_for_status()
        assert resp.json()["likes_count"] == count_after_like - 1

    async def test_get_liked_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Verify GET /me/liked/{item_id} returns the item."""
        item = bob_items[0]

        resp = await alice_client.post(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.get(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()
        assert resp.json()["id"] == item.id

    async def test_like_non_existent_item(
        self,
        alice_client: AsyncClient,
    ):
        """Liking a non-existent item should return 404."""
        resp = await alice_client.post("/api/v1/me/liked/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_unlike_non_liked_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Unliking a non-liked item should return 404."""
        item = bob_items[-1]
        resp = await alice_client.delete(f"/api/v1/me/liked/{item.id}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_like_item_twice(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        """Liking the same item twice should be idempotent or return error."""
        item = bob_items[0]

        resp = await alice_client.post(f"/api/v1/me/liked/{item.id}")
        resp.raise_for_status()

        resp = await alice_client.post(f"/api/v1/me/liked/{item.id}")
        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_409_CONFLICT,
        )
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/item/test_item_like_operations.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/item/test_item_like_operations.py
git commit -m "test: add like/unlike operation tests"
```

---

## Task 4: Borrowing endpoint bug fix + tests

**Files:**
- Modify: `app/routers/v1/me/borrowings/read.py:28-35`
- Modify: `tests/loan/test_loans_read.py`

- [ ] **Step 1: Write borrowing tests that expose the bug**

Add to the end of `tests/loan/test_loans_read.py`:

```python
class TestBorrowingRead:
    """Test borrowing read endpoints."""

    async def test_get_single_borrowing(
        self,
        bob_client: AsyncClient,
        alice_many_loans: list[LoanRead],
    ):
        """Borrower can fetch their own borrowing."""
        # find a loan where bob is borrower
        loan = next(
            loan for loan in alice_many_loans
            if loan.active
        )
        resp = await bob_client.get(f"/api/v1/me/borrowings/{loan.id}")
        resp.raise_for_status()
        assert resp.json()["id"] == loan.id

    async def test_get_single_borrowing_not_borrower(
        self,
        carol_client: AsyncClient,
        alice_many_loans: list[LoanRead],
    ):
        """Non-borrower cannot fetch someone else's borrowing."""
        loan = alice_many_loans[0]
        resp = await carol_client.get(f"/api/v1/me/borrowings/{loan.id}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
```

Also add missing imports at the top of the file:

```python
from fastapi import status
```

- [ ] **Step 2: Run test to confirm the bug**

Run: `pytest tests/loan/test_loans_read.py::TestBorrowingRead::test_get_single_borrowing -v`
Expected: FAIL — the endpoint uses `owner_id=client_id` instead of `borrower_id=client_id`, so Bob (borrower) gets 404.

- [ ] **Step 3: Fix the bug in the borrowing router**

In `app/routers/v1/me/borrowings/read.py`, change the `get_client_borrowing` function:

```python
@router.get("/{loan_id}", status_code=status.HTTP_200_OK)
async def get_client_borrowing(
    client_id: client_id_annotation,
    loan_id: loan_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoanRead:
    """Get loan where the client is the borrower."""
    return await services.loan.get_loan(
        db=db,
        loan_id=loan_id,
        query_filter=LoanReadQueryFilter(borrower_id=client_id),
    )
```

The change: `LoanReadQueryFilter(owner_id=client_id)` → `LoanReadQueryFilter(borrower_id=client_id)` and docstring updated.

- [ ] **Step 4: Run tests to verify fix**

Run: `pytest tests/loan/test_loans_read.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/loan/test_loans_read.py app/routers/v1/me/borrowings/read.py
git commit -m "fix: borrowing endpoint used owner_id instead of borrower_id

The get_client_borrowing endpoint was filtering by owner_id,
preventing borrowers from fetching their own borrowings."
```

---

## Task 5: Report email sender

**Files:**
- Create: `app/clients/email/report.py`
- Modify: `app/clients/email/__init__.py`

- [ ] **Step 1: Create the report email sender**

Create `app/clients/email/report.py`:

```python
from fastapi_mail import FastMail, MessageSchema, MessageType

from app.enums import ReportType


async def send_report_email(
    email_client: FastMail,
    *,
    app_name: str,
    moderator_email: str,
    report_type: ReportType,
    reporter_name: str,
    description: str,
    context: str,
    saved_info: str,
) -> None:
    """Send a report notification email to moderators."""

    message = MessageSchema(
        subject=f"[{app_name}] New {report_type.name} report",
        recipients=[moderator_email],
        body=(
            f"<h2>New {report_type.name} report</h2>"
            f"<p><b>Reporter:</b> {reporter_name}</p>"
            f"<p><b>Description:</b> {description}</p>"
            f"<p><b>Context:</b> {context}</p>"
            f"<hr>"
            f"<h3>Saved info</h3>"
            f"<pre>{saved_info}</pre>"
        ),
        subtype=MessageType.html,
    )

    await email_client.send_message(message)
```

- [ ] **Step 2: Export from `app/clients/email/__init__.py`**

Add to `app/clients/email/__init__.py`:

```python
from .report import send_report_email
```

And add `"send_report_email"` to the `__all__` list.

- [ ] **Step 3: Commit**

```bash
git add app/clients/email/report.py app/clients/email/__init__.py
git commit -m "feat: add report email sender for moderator notifications"
```

---

## Task 6: Implement report_user service

**Files:**
- Modify: `app/services/user/report.py`
- Reference: `app/models/report.py`, `app/models/user.py`

- [ ] **Step 1: Implement the report_user service**

Replace the content of `app/services/user/report.py`:

```python
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.email.report import send_report_email
from app.enums import ReportType
from app.models.report import Report
from app.schemas.report.create import ReportCreate
from app.services.user.read import get_user_private


async def report_user(
    db: AsyncSession,
    user_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
    *,
    email_client=None,
    app_name: str = "",
    moderator_email: str = "",
) -> None:
    """Create a report for the user with `user_id`.

    Snapshots the user's current state so evidence is preserved
    even if the user later modifies their profile.
    """

    # fetch user (raises UserNotFoundError if missing)
    user = await get_user_private(db=db, user_id=user_id)

    # fetch reporter name
    reporter = await get_user_private(db=db, user_id=reported_by_user_id)

    # snapshot user state
    saved_info = json.dumps(
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_seed": user.avatar_seed,
            "stars_count": user.stars_count,
            "validated": user.validated,
            "creation_date": str(user.creation_date),
        },
        ensure_ascii=False,
    )

    # create report
    report = Report(
        description=report_create.message,
        report_type=ReportType.user,
        created_by=reported_by_user_id,
        saved_info=saved_info,
        context=report_create.context,
    )
    db.add(report)

    # send email to moderators
    if email_client and moderator_email:
        await send_report_email(
            email_client,
            app_name=app_name,
            moderator_email=moderator_email,
            report_type=ReportType.user,
            reporter_name=reporter.name,
            description=report_create.message,
            context=report_create.context,
            saved_info=saved_info,
        )
```

- [ ] **Step 2: Update the router to pass email dependencies**

Check `app/routers/v1/users/read.py` — the current router just calls `services.user.report_user(db, user_id, reported_by_user_id, report_create)`. The service signature now has optional `email_client`, `app_name`, `moderator_email` kwargs. The existing call still works (email just won't send).

To wire email, update `app/routers/v1/users/read.py`'s `report_user` function:

```python
@router.post("/{user_id}/report", status_code=status.HTTP_201_CREATED)
async def report_user(
    client_id: client_id_annotation,
    user_id: user_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    app: Annotated[FastAPI, Depends(get_app)],
):
    """Report user."""
    return await services.user.report_user(
        db=db,
        user_id=user_id,
        reported_by_user_id=client_id,
        report_create=report_create,
        email_client=app.state.email_client if not app.state.config.test else None,
        app_name=app.state.config.app_name,
        moderator_email=app.state.config.email.from_email,
    )
```

Add imports:

```python
from fastapi import FastAPI
from app.database import get_app
```

- [ ] **Step 3: Commit**

```bash
git add app/services/user/report.py app/routers/v1/users/read.py
git commit -m "feat: implement report_user with state snapshot and email"
```

---

## Task 7: Implement report_item service

**Files:**
- Create: `app/services/item/report.py`
- Modify: `app/services/item/__init__.py`
- Modify: `app/routers/v1/items/report.py`

- [ ] **Step 1: Create the report_item service**

Create `app/services/item/report.py`:

```python
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.email.report import send_report_email
from app.enums import ReportType
from app.models.report import Report
from app.schemas.report.create import ReportCreate
from app.services.item.read import get_item
from app.services.user.read import get_user_private


async def report_item(
    db: AsyncSession,
    item_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
    *,
    email_client=None,
    app_name: str = "",
    moderator_email: str = "",
) -> None:
    """Create a report for the item with `item_id`.

    Snapshots the item's current state so evidence is preserved
    even if the item is later modified.
    """

    # fetch item (raises ItemNotFoundError if missing)
    item = await get_item(db=db, item_id=item_id)

    # fetch reporter name
    reporter = await get_user_private(db=db, user_id=reported_by_user_id)

    # snapshot item state
    saved_info = json.dumps(
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "targeted_age_months": str(item.targeted_age_months),
            "owner": {
                "id": item.owner.id,
                "name": item.owner.name,
            },
            "region_ids": list(item.region_ids),
            "image_names": item.image_names,
            "available": item.available,
            "creation_date": str(item.creation_date),
            "update_date": str(item.update_date),
        },
        ensure_ascii=False,
    )

    # create report
    report = Report(
        description=report_create.message,
        report_type=ReportType.item,
        created_by=reported_by_user_id,
        saved_info=saved_info,
        context=report_create.context,
    )
    db.add(report)

    # send email
    if email_client and moderator_email:
        await send_report_email(
            email_client,
            app_name=app_name,
            moderator_email=moderator_email,
            report_type=ReportType.item,
            reporter_name=reporter.name,
            description=report_create.message,
            context=report_create.context,
            saved_info=saved_info,
        )
```

- [ ] **Step 2: Export from `app/services/item/__init__.py`**

Add import:

```python
from .report import report_item
```

Add `"report_item"` to the `__all__` list.

- [ ] **Step 3: Update the item report router**

Replace the content of `app/routers/v1/items/report.py`:

```python
from typing import Annotated

from fastapi import Body, Depends, FastAPI, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_app, get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.report.create import ReportCreate

from .annotations import item_id_annotation
from .router import router


@router.post("/{item_id}/report", status_code=status.HTTP_201_CREATED)
async def report_item(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report creation fields."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    app: Annotated[FastAPI, Depends(get_app)],
):
    """Report the specified item."""
    return await services.item.report_item(
        db=db,
        item_id=item_id,
        reported_by_user_id=client_id,
        report_create=report_create,
        email_client=app.state.email_client if not app.state.config.test else None,
        app_name=app.state.config.app_name,
        moderator_email=app.state.config.email.from_email,
    )
```

- [ ] **Step 4: Commit**

```bash
git add app/services/item/report.py app/services/item/__init__.py app/routers/v1/items/report.py
git commit -m "feat: implement report_item with state snapshot and email"
```

---

## Task 8: Implement report_chat service

**Files:**
- Modify: `app/services/chat/chat/report.py`
- Reference: `app/services/chat/message/read.py`, `app/services/chat/chat/read.py`

- [ ] **Step 1: Implement the report_chat service**

Replace the content of `app/services/chat/chat/report.py`:

```python
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.email.report import send_report_email
from app.enums import ReportType
from app.models.report import Report
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatMessageReadQueryFilter, ChatReadQueryFilter
from app.schemas.report.create import ReportCreate
from app.services.chat.chat.read import get_chat
from app.services.chat.message.read import list_messages
from app.services.user.read import get_user_private


async def report_chat(
    db: AsyncSession,
    chat_id: ChatId,
    *,
    query_filter: ChatReadQueryFilter | None = None,
    reported_by_user_id: int,
    report_create: ReportCreate,
    email_client=None,
    app_name: str = "",
    moderator_email: str = "",
):
    """Create a report for the chat with `chat_id`.

    Snapshots all messages, members, and item info so evidence
    is preserved even if messages are later deleted or modified.
    """

    # fetch chat (raises ChatNotFoundError if missing / not member)
    chat = await get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=query_filter,
    )

    # fetch all messages in the chat
    messages_result = await list_messages(
        db=db,
        query_filter=ChatMessageReadQueryFilter(
            chat_id=chat_id,
            member_id=reported_by_user_id,
        ),
    )
    messages = messages_result.data

    # fetch reporter name
    reporter = await get_user_private(db=db, user_id=reported_by_user_id)

    # snapshot chat state
    saved_info = json.dumps(
        {
            "chat_id": str(chat.id),
            "item": {
                "id": chat.item.id,
                "name": chat.item.name,
            },
            "owner": {
                "id": chat.owner.id,
                "name": chat.owner.name,
            },
            "borrower": {
                "id": chat.borrower.id,
                "name": chat.borrower.name,
            },
            "messages": [
                {
                    "id": msg.id,
                    "sender_id": msg.sender_id,
                    "text": msg.text,
                    "message_type": msg.message_type.name,
                    "creation_date": str(msg.creation_date),
                    "seen": msg.seen,
                }
                for msg in messages
            ],
        },
        ensure_ascii=False,
    )

    # create report
    report = Report(
        description=report_create.message,
        report_type=ReportType.chat,
        created_by=reported_by_user_id,
        saved_info=saved_info,
        context=report_create.context,
    )
    db.add(report)

    # send email
    if email_client and moderator_email:
        await send_report_email(
            email_client,
            app_name=app_name,
            moderator_email=moderator_email,
            report_type=ReportType.chat,
            reporter_name=reporter.name,
            description=report_create.message,
            context=report_create.context,
            saved_info=saved_info,
        )
```

- [ ] **Step 2: Update the chat report router to pass email dependencies**

In `app/routers/v1/me/chats/report.py`, update the function:

```python
from typing import Annotated

from fastapi import Body, Depends, FastAPI, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_app, get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatReadQueryFilter
from app.schemas.report.create import ReportCreate

from .annotations import chat_id_annotation
from .router import router


@router.post(
    "/{chat_id}/report",
    status_code=status.HTTP_201_CREATED,
)
async def report_client_chat(
    client_id: client_id_annotation,
    chat_id: chat_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    app: Annotated[FastAPI, Depends(get_app)],
):
    """Report client's chat by id."""
    parsed_chat_id = ChatId.model_validate(chat_id)

    return await services.chat.report_chat(
        db=db,
        chat_id=parsed_chat_id,
        query_filter=ChatReadQueryFilter(member_id=client_id),
        reported_by_user_id=client_id,
        report_create=report_create,
        email_client=app.state.email_client if not app.state.config.test else None,
        app_name=app.state.config.app_name,
        moderator_email=app.state.config.email.from_email,
    )
```

- [ ] **Step 3: Commit**

```bash
git add app/services/chat/chat/report.py app/routers/v1/me/chats/report.py
git commit -m "feat: implement report_chat with message snapshot and email"
```

---

## Task 9: Report tests

**Files:**
- Create: `tests/test_report.py`

- [ ] **Step 1: Write report tests**

```python
import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.enums import ReportType
from app.models.report import Report
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.private import UserPrivateRead


@pytest.mark.usefixtures("items")
class TestReportUser:
    """Test user report endpoint."""

    async def test_report_user(
        self,
        alice_client: AsyncClient,
        bob: UserPrivateRead,
        database_sessionmaker: async_sessionmaker,
    ):
        """Report a user, verify DB row and snapshot content."""
        resp = await alice_client.post(
            f"/api/v1/users/{bob.id}/report",
            json={"message": "Inappropriate behavior", "context": "In chat"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.user)
                )
            ).scalars().all()
            assert len(reports) >= 1
            report = reports[-1]
            assert report.description == "Inappropriate behavior"
            assert report.context == "In chat"
            info = json.loads(report.saved_info)
            assert info["name"] == bob.name
            assert info["email"] == bob.email

    async def test_report_user_snapshot_preserved(
        self,
        alice_client: AsyncClient,
        bob: UserPrivateRead,
        bob_client: AsyncClient,
        database_sessionmaker: async_sessionmaker,
    ):
        """Snapshot preserves original name even after user changes it."""
        original_name = bob.name

        resp = await alice_client.post(
            f"/api/v1/users/{bob.id}/report",
            json={"message": "Bad content", "context": "Profile"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # bob changes name
        resp = await bob_client.post(
            "/api/v1/me",
            json={"name": "newbobname"},
        )
        resp.raise_for_status()

        # verify snapshot still has original name
        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.user)
                )
            ).scalars().all()
            report = reports[-1]
            info = json.loads(report.saved_info)
            assert info["name"] == original_name

    async def test_report_non_existent_user(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.post(
            "/api/v1/users/999999/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_report_user_no_auth(
        self,
        client: AsyncClient,
        bob: UserPrivateRead,
    ):
        resp = await client.post(
            f"/api/v1/users/{bob.id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_report_user_empty_message(
        self,
        alice_client: AsyncClient,
        bob: UserPrivateRead,
    ):
        """Empty message should return 422."""
        resp = await alice_client.post(
            f"/api/v1/users/{bob.id}/report",
            json={"message": "", "context": ""},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("items")
class TestReportItem:
    """Test item report endpoint."""

    async def test_report_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
        database_sessionmaker: async_sessionmaker,
    ):
        """Report an item, verify snapshot contains item details."""
        item = bob_items[0]

        resp = await alice_client.post(
            f"/api/v1/items/{item.id}/report",
            json={"message": "Policy violation", "context": "Item listing"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.item)
                )
            ).scalars().all()
            assert len(reports) >= 1
            report = reports[-1]
            info = json.loads(report.saved_info)
            assert info["id"] == item.id
            assert info["name"] == item.name
            assert info["description"] == item.description
            assert "owner" in info
            assert info["owner"]["id"] == item.owner.id

    async def test_report_item_snapshot_preserved(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
        database_sessionmaker: async_sessionmaker,
    ):
        """Snapshot preserves original name after item is updated."""
        original_name = alice_new_item.name

        resp = await alice_client.post(
            f"/api/v1/items/{alice_new_item.id}/report",
            json={"message": "Bad content", "context": "Listing"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # update item name
        resp = await alice_client.post(
            f"/api/v1/me/items/{alice_new_item.id}",
            json={"name": "updated-item-name"},
        )
        resp.raise_for_status()

        # verify snapshot still has original name
        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.item)
                )
            ).scalars().all()
            report = reports[-1]
            info = json.loads(report.saved_info)
            assert info["name"] == original_name

    async def test_report_non_existent_item(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.post(
            "/api/v1/items/999999/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_report_item_no_auth(
        self,
        client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        resp = await client.post(
            f"/api/v1/items/{bob_items[0].id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestReportChat:
    """Test chat report endpoint."""

    async def test_report_chat(
        self,
        alice_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        database_sessionmaker: async_sessionmaker,
    ):
        """Report a chat, verify snapshot contains messages and members."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        resp = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/report",
            json={"message": "Harassment", "context": "Chat conversation"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.chat)
                )
            ).scalars().all()
            assert len(reports) >= 1
            report = reports[-1]
            info = json.loads(report.saved_info)
            assert "messages" in info
            assert len(info["messages"]) >= 1
            assert "owner" in info
            assert "borrower" in info
            assert "item" in info

    async def test_report_chat_not_member(
        self,
        carol_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Non-member cannot report a chat."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        resp = await carol_client.post(
            f"/api/v1/me/chats/{chat_id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.is_error

    async def test_report_non_existent_chat(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.post(
            "/api/v1/me/chats/999999-999999/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.is_error

    async def test_report_chat_no_auth(
        self,
        client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        resp = await client.post(
            f"/api/v1/me/chats/{chat_id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_report.py -v`
Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_report.py
git commit -m "test: add report tests for user, item, and chat"
```

---

## Task 10: Pagination edge case tests

**Files:**
- Create: `tests/test_pagination_edge_cases.py`

- [ ] **Step 1: Write pagination edge case tests**

```python
import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.user.private import UserPrivateRead


@pytest.mark.usefixtures("items")
class TestPaginationEdgeCases:
    """Test pagination boundary conditions on representative endpoints."""

    @pytest.mark.parametrize("limit", [0, -1])
    async def test_limit_invalid_items(
        self,
        client: AsyncClient,
        limit: int,
    ):
        """Zero or negative limit should return 422."""
        resp = await client.get("/api/v1/items", params={"n": limit})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_limit_exceeds_max_items(
        self,
        client: AsyncClient,
    ):
        """Limit > 256 should return 422."""
        resp = await client.get("/api/v1/items", params={"n": 257})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_limit_at_max_items(
        self,
        client: AsyncClient,
    ):
        """Limit == 256 should succeed."""
        resp = await client.get("/api/v1/items", params={"n": 256})
        resp.raise_for_status()

    async def test_empty_collection_items(
        self,
        alice_client: AsyncClient,
    ):
        """Querying items with impossible filter returns empty list."""
        resp = await alice_client.get(
            "/api/v1/me/saved",
        )
        resp.raise_for_status()
        assert resp.json() == []

    @pytest.mark.parametrize("limit", [0, -1])
    async def test_limit_invalid_chats(
        self,
        alice_client: AsyncClient,
        limit: int,
    ):
        resp = await alice_client.get("/api/v1/me/chats", params={"n": limit})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_limit_exceeds_max_chats(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.get("/api/v1/me/chats", params={"n": 257})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("limit", [0, -1])
    async def test_limit_invalid_loans(
        self,
        alice_client: AsyncClient,
        limit: int,
    ):
        resp = await alice_client.get("/api/v1/me/loans", params={"n": limit})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_limit_exceeds_max_loans(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.get("/api/v1/me/loans", params={"n": 257})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_pagination_edge_cases.py -v`
Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_pagination_edge_cases.py
git commit -m "test: add pagination edge case tests"
```

---

## Task 11: Malformed input tests

**Files:**
- Create: `tests/test_edge_cases.py`

- [ ] **Step 1: Write malformed input tests**

```python
import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.loan.read import LoanRequestRead


class TestMalformedInputs:
    """Test malformed inputs return proper error responses."""

    async def test_invalid_chat_id_format(
        self,
        alice_client: AsyncClient,
    ):
        """Invalid chat_id format should return 422."""
        resp = await alice_client.get("/api/v1/me/chats/invalid")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_non_integer_item_id(
        self,
        client: AsyncClient,
    ):
        """Non-integer item_id should return 422."""
        resp = await client.get("/api/v1/items/abc")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_empty_text_message(
        self,
        alice_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Empty text message should be rejected."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        resp = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": ""},
        )
        assert resp.is_error
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_edge_cases.py -v`
Expected: All tests PASS (or reveal missing validation — fix if needed).

- [ ] **Step 3: Commit**

```bash
git add tests/test_edge_cases.py
git commit -m "test: add malformed input edge case tests"
```

---

## Task 12: Token edge case tests

**Files:**
- Modify: `tests/test_auth.py`

- [ ] **Step 1: Add token edge case tests**

Add these test classes at the end of `tests/test_auth.py`:

```python
import jwt


@pytest.mark.usefixtures("alice")
class TestAuthTokenEdgeCases:
    """Test token validation edge cases."""

    async def test_expired_access_token(
        self,
        client: AsyncClient,
        app_config,
    ):
        """Expired JWT should return 401."""
        from datetime import UTC, datetime, timedelta

        expired_token = jwt.encode(
            {
                "iat": datetime.now(UTC) - timedelta(hours=2),
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "sub": "1",
                "validated": True,
            },
            key=app_config.auth.secret_key,
            algorithm=app_config.auth.algorithm,
        )
        resp = await client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_malformed_jwt(
        self,
        client: AsyncClient,
    ):
        """Garbage Bearer token should return 401."""
        resp = await client.get(
            "/api/v1/me",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_bad_signature_jwt(
        self,
        client: AsyncClient,
        app_config,
    ):
        """JWT signed with wrong key should return 401."""
        from datetime import UTC, datetime, timedelta

        bad_token = jwt.encode(
            {
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "sub": "1",
                "validated": True,
            },
            key="wrong-secret-key",
            algorithm=app_config.auth.algorithm,
        )
        resp = await client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
```

- [ ] **Step 2: Add jwt import at top of file**

Add `import jwt` to the imports at the top of `tests/test_auth.py`.

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_auth.py::TestAuthTokenEdgeCases -v`
Expected: All 3 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_auth.py
git commit -m "test: add token edge case tests (expired, malformed, bad signature)"
```

---

## Task 13: WebSocket tests

**Files:**
- Create: `tests/test_websocket.py`

- [ ] **Step 1: Write WebSocket tests**

```python
import jwt
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession, aconnect_ws

from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import (
    WebSocketMessageNewChatMessage,
    WebSocketMessageUpdatedChatMessage,
    WebSocketMessageTypeAdapter,
)
from tests.fixtures.clients import create_client, login_as_user
from tests.fixtures.users import UserData
from tests.fixtures.websockets import WebSocketRecorder


class TestWebSocketAuth:
    """Test WebSocket authentication."""

    async def test_websocket_no_auth(
        self,
        app: FastAPI,
    ):
        """Connection without credentials should be rejected."""
        client = create_client(app)
        async with client:
            with pytest.raises(Exception):
                async with aconnect_ws("/api/v1/me/websocket", client):
                    pass

    async def test_websocket_expired_token(
        self,
        app: FastAPI,
        app_config,
    ):
        """Connection with expired JWT should be rejected."""
        from datetime import UTC, datetime, timedelta

        expired_token = jwt.encode(
            {
                "iat": datetime.now(UTC) - timedelta(hours=2),
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "sub": "1",
                "validated": True,
            },
            key=app_config.auth.secret_key,
            algorithm=app_config.auth.algorithm,
        )
        client = create_client(app)
        async with client:
            client.cookies.set("Authorization", f"Bearer {expired_token}")
            with pytest.raises(Exception):
                async with aconnect_ws("/api/v1/me/websocket", client):
                    pass

    async def test_websocket_malformed_token(
        self,
        app: FastAPI,
    ):
        """Connection with bad token should be rejected."""
        client = create_client(app)
        async with client:
            client.cookies.set("Authorization", "Bearer garbage.token.here")
            with pytest.raises(Exception):
                async with aconnect_ws("/api/v1/me/websocket", client):
                    pass


class TestWebSocketRelay:
    """Test WebSocket message relay."""

    async def test_websocket_new_message_relay(
        self,
        alice_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """New chat message is relayed via WebSocket."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # drain pending messages from fixture setup
        try:
            while True:
                await alice_websocket.receive_text(timeout=0.5)
        except TimeoutError:
            pass

        recorder = WebSocketRecorder(alice_websocket)
        async with recorder:
            resp = await bob_client.post(
                f"/api/v1/me/chats/{chat_id}/messages",
                json={"text": "hello from bob"},
            )
            resp.raise_for_status()

        assert any(
            isinstance(msg, WebSocketMessageNewChatMessage)
            for msg in recorder.messages
        ), f"Expected WebSocketMessageNewChatMessage, got: {[type(m).__name__ for m in recorder.messages]}"

    async def test_websocket_seen_update_relay(
        self,
        alice: UserPrivateRead,
        alice_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_client: AsyncClient,
        bob_websocket: AsyncWebSocketSession,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Marking a message as seen is relayed via WebSocket."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        # send a message
        resp = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": "test seen"},
        )
        resp.raise_for_status()
        message_id = resp.json()["id"]

        # drain pending messages
        for ws in [alice_websocket, bob_websocket]:
            try:
                while True:
                    await ws.receive_text(timeout=0.5)
            except TimeoutError:
                pass

        recorder_alice = WebSocketRecorder(alice_websocket)
        recorder_bob = WebSocketRecorder(bob_websocket)

        async with recorder_alice, recorder_bob:
            resp = await bob_client.post(
                f"/api/v1/me/chats/{chat_id}/messages/{message_id}/see"
            )
            resp.raise_for_status()

        for recorder in [recorder_alice, recorder_bob]:
            assert any(
                isinstance(msg, WebSocketMessageUpdatedChatMessage)
                for msg in recorder.messages
            ), f"Expected WebSocketMessageUpdatedChatMessage, got: {[type(m).__name__ for m in recorder.messages]}"


class TestWebSocketIsolation:
    """Test WebSocket channel isolation."""

    async def test_websocket_isolation(
        self,
        alice_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
        carol_client: AsyncClient,
        carol_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Only chat members receive WebSocket notifications."""
        chat_id = carol_new_loan_request_for_alice_new_item.chat_id

        # drain pending messages
        for ws in [alice_websocket, bob_websocket]:
            try:
                while True:
                    await ws.receive_text(timeout=0.5)
            except TimeoutError:
                pass

        recorder_alice = WebSocketRecorder(alice_websocket)
        recorder_bob = WebSocketRecorder(bob_websocket)

        async with recorder_alice, recorder_bob:
            resp = await carol_client.post(
                f"/api/v1/me/chats/{chat_id}/messages",
                json={"text": "carol to alice"},
            )
            resp.raise_for_status()

        # Alice should have received the message (she's in the chat)
        assert any(
            isinstance(msg, WebSocketMessageNewChatMessage)
            for msg in recorder_alice.messages
        ), "Alice should receive the message"

        # Bob should NOT have received anything
        assert not any(
            isinstance(msg, WebSocketMessageNewChatMessage)
            for msg in recorder_bob.messages
        ), f"Bob should not receive messages, got: {[type(m).__name__ for m in recorder_bob.messages]}"
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_websocket.py -v`
Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_websocket.py
git commit -m "test: add WebSocket auth, relay, and isolation tests"
```

---

## Task 14: Full test suite verification

- [ ] **Step 1: Run the full test suite**

Run: `pytest -n logical --dist loadscope --maxfail=5`
Expected: All tests PASS (except possible imgpush rate limit errors which are external).

- [ ] **Step 2: Run linter**

Run: `ruff check .`
Expected: No errors.

- [ ] **Step 3: Run type checker**

Run: `mypy stubs app seed tests`
Expected: No new errors.

- [ ] **Step 4: Final commit if any fixups needed**

```bash
git add -u
git commit -m "fix: address lint/type issues from test coverage work"
```
