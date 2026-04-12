# Test Coverage Improvement & Report Features

## Goal

Fill test coverage gaps for existing untested features, implement the report system (user/item/chat), add edge case and robustness tests, and add targeted WebSocket tests.

## Approach

Test-first for existing features, then implement reports with tests, then edge cases, then WebSocket tests.

---

## Phase 1: Tests for existing untested features

### 1.1 Stars service (`app/services/user/star/update.py`, `app/domain/star.py`)

New test file: `tests/user/test_user_stars.py`

- `test_add_stars_to_user` — call `add_stars_to_user(user_id, count=10)`, verify `stars_count` incremented by 10
- `test_add_many_stars_to_users` — batch update for alice and bob, verify each gets correct count
- `test_add_stars_duplicate_user_raises` — pass same user_id twice in batch, expect `ValueError`
- `test_add_stars_non_existent_user_raises` — pass non-existent user_id, expect `UserNotFoundError`
- `test_stars_gain_when_adding_item` — unit test for domain function: `stars_gain_when_adding_item(1)` returns 20, `(3)` returns 60
- `test_stars_gain_invalid_input` — non-integer input raises `ValueError`

### 1.2 Saved items (add/remove/list)

New test file: `tests/item/test_item_save.py`

Endpoints: `POST /me/saved/{item_id}`, `GET /me/saved`, `GET /me/saved/{item_id}`, `DELETE /me/saved/{item_id}`

- `test_save_item` — Alice saves Bob's item, verify it appears in `GET /me/saved`
- `test_unsave_item` — Alice saves then unsaves, verify it disappears from list
- `test_get_saved_item` — Verify `GET /me/saved/{item_id}` returns the item
- `test_save_non_existent_item` — Expect 404
- `test_unsave_non_saved_item` — Expect 404
- `test_save_item_twice` — Verify behavior (idempotent 200 or 409 conflict)

### 1.3 Liked items (add/remove)

New test file: `tests/item/test_item_like_operations.py` (existing `test_item_like.py` only tests pagination)

Endpoints: `POST /me/liked/{item_id}`, `GET /me/liked/{item_id}`, `DELETE /me/liked/{item_id}`

- `test_like_item` — Alice likes Bob's item, verify it appears in `GET /me/liked` and `likes_count` increments
- `test_unlike_item` — Alice likes then unlikes, verify removed and count decrements
- `test_get_liked_item` — Verify `GET /me/liked/{item_id}` returns the item
- `test_like_non_existent_item` — Expect 404
- `test_unlike_non_liked_item` — Expect 404
- `test_like_item_twice` — Verify behavior (idempotent or error)

### 1.4 Borrowing endpoint bug check

Add to `tests/loan/test_loans_read.py`:

- `test_get_single_borrowing` — Bob borrows from Alice, fetches `GET /me/borrowings/{loan_id}`, should succeed
- `test_get_single_borrowing_not_borrower` — Carol tries to fetch Bob's borrowing via `GET /me/borrowings/{loan_id}`, should fail

If the explore's suspicion is correct (`owner_id` used instead of `borrower_id` in the filter), this test will expose it.

---

## Phase 2: Report features implementation + tests

### 2.1 Implementation

The `Report` model already exists with fields: `id`, `description`, `report_type` (user/item/chat), `created_by`, `creation_date`, `saved_info`, `context`.

The `ReportCreate` schema has: `message`, `context`.

Alembic migration: verify the `report` table exists. If not, generate a migration.

#### Service: `report_user` (`app/services/user/report.py`)

Fill the empty stub:

1. Fetch user by `user_id` (raise `UserNotFoundError` if missing)
2. Build `saved_info` JSON snapshot:
   - `id`, `name`, `email`, `avatar_seed`, `stars_count`, `items_count`, `validated`, `creation_date`
3. Create `Report` row: `description=report_create.message`, `report_type=ReportType.user`, `created_by=reported_by_user_id`, `saved_info=json.dumps(snapshot)`, `context=report_create.context`
4. Send moderator email with report details (use existing email client from `app.state`)

#### Service: `report_item` (new file `app/services/item/report.py`)

1. Fetch item by `item_id` with owner + images eagerly loaded (raise `ItemNotFoundError` if missing)
2. Build `saved_info` JSON snapshot:
   - `id`, `name`, `description`, `targeted_age_months`, `region` (id + name), `owner` (id + name), `images` (list of filenames/URLs), `available`, `creation_date`, `update_date`
3. Create `Report` row with `report_type=ReportType.item`
4. Send moderator email

Register in `app/services/item/__init__.py`.

#### Service: `report_chat` (`app/services/chat/chat/report.py`)

Replace the `NotImplementedError` stub:

1. Fetch chat by `chat_id` with membership check via `query_filter` (raise `ChatNotFoundError` if missing)
2. Fetch all messages in the chat
3. Build `saved_info` JSON snapshot:
   - `chat_id`, `item` (id + name), `owner` (id + name), `borrower` (id + name)
   - `messages`: list of `{id, sender_id, sender_name, text, message_type, creation_date, seen}`
4. Create `Report` row with `report_type=ReportType.chat`
5. Send moderator email

#### Email to moderators

Add a `send_report_email` function (or extend existing email client) that sends:
- Subject: `"[Babytroc] New {type} report"`
- Body: Reporter info, reported entity summary, description, context, full `saved_info` dump

The email destination should use a configurable moderator email address (add `MODERATOR_EMAIL` to `Config` or reuse `EMAIL_FROM_EMAIL`).

### 2.2 Tests

New test file: `tests/test_report.py`

#### User report
- `test_report_user` — Alice reports Bob, verify 201, verify `Report` row in DB with correct `report_type=user`, verify `saved_info` contains Bob's name/email/stars_count
- `test_report_user_snapshot_preserved` — Alice reports Bob, Bob changes name, verify `saved_info` still has original name
- `test_report_non_existent_user` — Expect 404
- `test_report_user_no_auth` — Expect 401
- `test_report_user_empty_message` — Expect 422

#### Item report
- `test_report_item` — Alice reports Bob's item, verify 201, verify `saved_info` contains item name/description/images/owner
- `test_report_item_snapshot_preserved` — Report item, then update item name, verify `saved_info` has original name
- `test_report_non_existent_item` — Expect 404
- `test_report_item_no_auth` — Expect 401

#### Chat report
- `test_report_chat` — Alice reports chat with Bob, verify 201, verify `saved_info` contains all messages + both members + item info
- `test_report_chat_not_member` — Carol tries to report Alice-Bob chat, expect 403/404
- `test_report_non_existent_chat` — Expect 404
- `test_report_chat_no_auth` — Expect 401

---

## Phase 3: Edge cases & robustness

### 3.1 Pagination edge cases

New test file: `tests/test_pagination_edge_cases.py`

Tested on 3 representative endpoints: items (`GET /items`), chats (`GET /me/chats`), loans (`GET /me/loans`).

Existing validation: `PageLimitField(nmax=256, gt=0)` — no implementation needed, just tests.

- `test_limit_zero` — `?n=0` → 422
- `test_limit_negative` — `?n=-1` → 422
- `test_limit_exceeds_max` — `?n=257` → 422
- `test_limit_at_max` — `?n=256` → succeeds
- `test_empty_collection` — query with no matching data → empty list (not error)
- `test_cursor_past_end` — paginate to a cursor beyond last page → empty list

### 3.2 Malformed inputs

Add to `tests/test_edge_cases.py` or inline in existing test files:

- `test_invalid_chat_id_format` — `GET /me/chats/invalid` → 422
- `test_non_integer_item_id` — `GET /items/abc` → 422
- `test_empty_text_message` — `POST /me/chats/{id}/messages` with `{"text": ""}` → 422
- `test_oversized_text_message` — 100KB text body → 422 or rejection

### 3.3 Token edge cases

Add to `tests/test_auth.py`:

- `test_expired_access_token` — Craft a JWT with `exp` in the past, send request → 401
- `test_malformed_jwt` — Send garbage string as Bearer token → 401
- `test_bad_signature_jwt` — Sign JWT with wrong secret → 401
- `test_refresh_invalidated_token` — Invalidate refresh token in DB, attempt refresh → 401
- `test_refresh_expired_token` — Create refresh token with old `creation_date`, attempt refresh → 401

---

## Phase 4: WebSocket tests

New test file: `tests/test_websocket.py`

### 4.1 Auth rejection
- `test_websocket_no_auth` — Connect to `/me/websocket` without credentials → connection rejected
- `test_websocket_expired_token` — Connect with expired JWT → connection rejected
- `test_websocket_malformed_token` — Connect with bad signature → connection rejected

### 4.2 Message relay
- `test_websocket_new_message_relay` — Alice connected via WS, Bob sends message in shared chat via REST → Alice receives `WebSocketMessageNewChatMessage`
- `test_websocket_seen_update_relay` — Alice sends message, Bob marks seen → both receive `WebSocketMessageUpdatedChatMessage`
- `test_websocket_account_validation` — User connects, account gets validated → receives `WebsocketMessageUpdatedAccountValidation`

### 4.3 Channel isolation
- `test_websocket_isolation` — Alice and Bob connected. Carol sends message to Alice. Verify Alice receives it, Bob does not (timeout on Bob's WS).

---

## Implementation order

1. Phase 1 (tests for existing features) — likely surfaces bugs
2. Phase 2 (report implementation + tests) — new feature
3. Phase 3 (edge cases) — hardening
4. Phase 4 (WebSocket tests) — targeted coverage

## Files created/modified

### New files
- `tests/user/test_user_stars.py`
- `tests/item/test_item_save.py`
- `tests/item/test_item_like_operations.py`
- `tests/test_report.py`
- `tests/test_pagination_edge_cases.py`
- `tests/test_websocket.py`
- `app/services/item/report.py`

### Modified files
- `app/services/user/report.py` — fill stub
- `app/services/chat/chat/report.py` — fill stub
- `app/services/item/__init__.py` — register report service
- `app/config.py` — add `MODERATOR_EMAIL` if needed
- `tests/loan/test_loans_read.py` — add borrowing endpoint tests
- `tests/test_auth.py` — add token edge case tests
