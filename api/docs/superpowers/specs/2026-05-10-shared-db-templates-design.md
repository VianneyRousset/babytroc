# Shared DB Templates — Design

## Problem

`tests/fixtures/database.py` builds a single primary database (`primary_database`,
session-scoped) by running alembic + a 200-line `_seed_template` that bakes
alice/bob/carol, 2 regions, 13 categories, and 7 PBM images. Every test then
clones that primary via `CREATE DATABASE … TEMPLATE`.

Two consequences:

1. **Heavy class-scoped fixtures rebuild from scratch every class.**
   `tests/item/`, `tests/loan/`, and `tests/chat_read/` override `database` to
   class scope, then class fixtures (`many_items`, `many_users`,
   `many_loan_requests_for_alice_items`, `alice_many_loans`,
   `some_items_with_french_names`, `alice_many_chats`) issue 256+ inserts at
   the start of every class. The pg `CREATE DATABASE … TEMPLATE` mechanism
   could clone these states instead, but only one template exists today.
2. **Tests that need no domain data still pay full seed cost.**
   `tests/test_cache*.py`, `tests/test_s3*.py`, `tests/shared/test_rate_limit.py`,
   `tests/infrastructure/test_*.py`, `tests/test_image_variants.py`,
   `tests/babycli/*.py` clone the full seeded DB even though they touch
   migrations only or no DB at all.

The seeder is also a single cross-domain function — there is no module
boundary between region/category seeding, user seeding, image seeding, item
seeding, or loan seeding.

## Goals

- A multi-level pg template chain. Each named template is built once per
  xdist worker by `CREATE DATABASE … TEMPLATE <parent>` plus a small seed
  step. Tests clone the cheapest template that has what they need.
- Per-domain seed code under `tests/fixtures/database/seeds/`, with cross-cutting
  pg admin and fixture lifecycle code under
  `tests/fixtures/database/infrastructure/`.
- Test classes pick a template via `@pytest.mark.db_template("…")`. Each test
  method gets its own clone of that template — full per-method isolation, no
  shared state between methods.
- All "extra setup beyond a named template" lives in the template chain
  itself. There is no per-class hook to run additional writes; if a class
  needs a unique state, that state becomes a named template.

## Non-goals

- Sharing templates across xdist workers. Each worker continues to build its
  own chain (current behavior).
- Reworking function-scoped fixtures that create a small amount of data
  (`bob_new_loan_request_for_alice_new_item` and similar). Those remain
  function-scoped Python fixtures.
- Unifying these test seeders with `babycli db seed`. The two have different
  determinism and scale needs.
- Changing how the FastAPI `app` fixture is wired or how
  `database_sessionmaker` swaps the app session maker.

## The template chain

Built once per xdist worker, in topological order:

```
tpl_bare                              migrations only
└── tpl_reference                     + 2 regions, 13 categories
    └── tpl_baseline                  + alice, bob, carol + 7 PBM images
        └── tpl_baseline_items        + alice_items, bob_items,
            │                           alice_new_item, alice_special_item
            ├── tpl_many_items        + 256 mixed Alice/Bob items
            │   ├── tpl_many_loan_requests
            │   │                     + varied-state requests on many_items
            │   │                       (cancelled, rejected, accepted,
            │   │                        executed, pending — ≥10 of each
            │   │                        non-executed state)
            │   └── tpl_alice_many_chats
            │                         + chats Alice↔Bob over many_items
            ├── tpl_alice_many_items  + 256 Alice-owned items
            │   └── tpl_alice_many_loans
            │                         + executed/ended/restarted loans
            ├── tpl_french_named_items
            │                         + ~53 French-named items
            └── tpl_many_users        + 256 random users
                └── tpl_alice_special_item_loan_requests
                                      + requests from many_users for
                                        alice_special_item
```

`tpl_baseline` is the default for tests that don't declare a marker (matches
today's `primary_database`). `tpl_bare` and `tpl_reference` exist so
infrastructure-only and reference-data-only tests can opt out of user/image
seeding.

### Why every class-scoped state is a named template

The user-facing rule is: a test class declares its template, and each method
gets a fresh clone of that template. There is no escape hatch for "do extra
setup at class level beyond the template". If a class needs a unique state,
that state must be added to the chain as a new template node.

This forces de-duplication: identical class setups across tests collapse to
a single template; one-off variations become explicit chain nodes that
others can reuse later.

The constraint that drives this: pg requires no active connections to a
template DB during `CREATE DATABASE … TEMPLATE`. Any "open class engine →
write extras → keep open across methods" pattern would block per-method
clones. By committing every class-level state to a named template, the
class-scoped engine is closed at chain-build time, before any method runs.

## Module layout

```
tests/fixtures/database/
├── __init__.py                 re-exports public fixtures
├── infrastructure/             cross-cutting plumbing
│   ├── __init__.py
│   ├── admin.py                create_database, drop_database,
│   │                           set_datallowconn, dispose_engine helpers
│   ├── chain.py                TemplateSpec, build_chain (topological
│   │                           build of all tpl_* dbs once per worker)
│   ├── lifecycle.py            primary_databases (session), database
│   │                           (function), database_sessionmaker fixtures
│   ├── marker.py               db_template marker reader
│   └── registry.py             TEMPLATES = {"bare": …, "baseline": …, …}
└── seeds/                      per-domain seed fns
    ├── __init__.py
    ├── region.py               seed_reference_regions
    ├── category.py             seed_reference_categories
    ├── user.py                 seed_baseline_users, seed_many_users
    ├── image.py                seed_baseline_images
    ├── item.py                 seed_baseline_items, seed_many_items,
    │                           seed_alice_many_items,
    │                           seed_french_named_items
    ├── loan.py                 seed_many_loan_requests_for_alice_items,
    │                           seed_alice_many_loans,
    │                           seed_alice_special_item_loan_requests
    └── chat.py                 seed_alice_many_chats
```

The split:

- **`infrastructure/`** owns pg admin (CREATE/DROP DATABASE, ALTER
  ALLOW_CONNECTIONS), fixture lifecycle, the chain build engine, the marker
  reader, and the registry that wires it all together. Nothing in this layer
  imports any `babytroc.domains.*` module.
- **`seeds/`** owns one async function per logical seed step, organized by
  the domain that owns the data. Each seed signature is roughly
  `async def seed_x(db: AsyncSession, *, ctx: SeedContext) -> None`, where
  `SeedContext` exposes a `Config` (for image upload) and any reference data
  the seed needs from earlier steps (e.g. user IDs, image names). Seeds
  import freely from `babytroc.domains.*` services and schemas.

## Lifecycle

### Per-worker, session scope

`infrastructure/chain.py::build_chain(base_url)` reads `infrastructure/registry.py::TEMPLATES`,
sorts topologically, and for each node:

1. `CREATE DATABASE "<unique-name>" TEMPLATE "<parent>"` (or `template1` for
   `tpl_bare`). Names include a per-worker suffix so xdist workers don't
   collide.
2. For `tpl_bare`, run alembic upgrade head against the new DB.
3. For all others, open an engine + session against the new DB, run the
   node's seed fns in declared order inside a single transaction,
   `await engine.dispose()`. Disposing matters: any leftover connection
   blocks downstream `CREATE DATABASE TEMPLATE` from this node.

Returns a mapping `{name: URL}` published as the `primary_databases`
session fixture.

Drops happen in reverse topological order at session teardown.

### Per-test, function scope

`infrastructure/lifecycle.py::database` reads the
`@pytest.mark.db_template("…")` marker on the closest class (defaulting to
`"baseline"`), looks up the parent URL in `primary_databases`, and clones:

```
CREATE DATABASE "test-<uuid>-<workerid>" TEMPLATE "<tpl_…>"
yield URL
DROP DATABASE …
```

`database_sessionmaker` builds an engine + sessionmaker for that URL, calls
`init_db_session_dependency(maker)` so the FastAPI app uses it for the
duration of the test, yields the maker, disposes the engine.

### Per-class, scope override

The current `tests/{item,loan,chat_read}/conftest.py` overrides of `database`
to class scope are removed. With per-method clones from rich templates the
old reason for the override (avoid 256-row rebuilds per method) no longer
applies.

If a future use case genuinely needs class-scope (e.g. a test that
benchmarks something across methods of the same DB), it can keep the local
override. The default flow does not need it.

## Test code changes

### Class declaration

```python
@pytest.mark.db_template("alice_many_loans")
class TestLoansRead:
    async def test_x(self, alice_many_loans, ...): ...
```

Untyped tests default to `db_template("baseline")` — bit-identical to the
current `_seed_template` content.

### Data-returning fixtures become SELECT fixtures

Today many class-scoped fixtures both *create* and *return* objects:

```python
@pytest.fixture(scope="class")
async def many_items(db_sessionmaker, alice, bob, ...) -> list[ItemRead]:
    # 256 inserts, returns the inserted ItemRead list
```

After this change the inserts move into a chain seed; the fixture becomes a
plain `SELECT`:

```python
@pytest.fixture
async def many_items(database_sessionmaker) -> list[ItemRead]:
    async with database_sessionmaker.begin() as session:
        rows = (await session.execute(select(Item))).scalars().all()
        return [ItemRead.model_validate(r) for r in rows]
```

Same call sites in tests; same return type. This applies to: `many_items`,
`alice_many_items`, `many_users`, `some_items_with_french_names`,
`many_loan_requests_for_alice_items`,
`many_loan_requests_for_alice_special_item`, `alice_many_loans`,
`alice_many_chats`. Existing fixtures `alice_new_item`,
`alice_special_item`, `alice_items`, `bob_items`, `alice_items_image`,
`bob_items_image`, `alice_new_item_images`, `alice_special_item_images` are
already SELECT-style or close to it; their bodies move to the seed and the
fixture becomes a query.

Function-scoped fixtures that build a small amount of data on top of the
class state (`bob_new_loan_request_for_alice_new_item`,
`bob_accepted_loan_request_for_alice_special_item`,
`bob_new_loan_for_alice_special_item`, `carol_new_loan_request_for_alice_new_item`,
`bob_new_loan_of_alice_new_item`, `alice_many_messages_to_bob`) stay as
function fixtures — they intentionally exercise create-paths inside the
test scope.

### conftest deletions

`tests/item/conftest.py`, `tests/loan/conftest.py`,
`tests/chat_read/conftest.py` lose their `database` /
`database_sessionmaker` / per-class re-readers and become either empty
(remove the file) or shrink to nothing.

## Migration plan

Each step is a self-contained PR. Tests pass at every step.

1. **Infrastructure + 3-node chain.**
   Land `tests/fixtures/database/` package with `infrastructure/` and an
   empty `seeds/`. Move `_seed_template` content into
   `seeds/{region,category,user,image}.py`. Register `tpl_bare`,
   `tpl_reference`, `tpl_baseline`. Marker reader defaults to `baseline`.
   Existing tests pass unchanged.
2. **`tpl_baseline_items`.** Move alice/bob baseline items, alice_new_item,
   alice_special_item into `seeds/item.py::seed_baseline_items`. Convert the
   item/image fixtures in `tests/fixtures/items.py` to SELECT fixtures.
3. **`tpl_many_items` + `tpl_alice_many_items` + `tpl_french_named_items`.**
   Migrate `tests/item/` to markers, delete `tests/item/conftest.py`
   overrides. Convert `many_items`, `alice_many_items`,
   `some_items_with_french_names` to SELECT fixtures.
4. **`tpl_many_loan_requests` + `tpl_alice_many_loans` +
   `tpl_alice_special_item_loan_requests` + `tpl_many_users`.** Migrate
   `tests/loan/`, delete `tests/loan/conftest.py` overrides. Convert loan +
   user-bulk fixtures to SELECT.
5. **`tpl_alice_many_chats`.** Migrate `tests/chat_read/`, delete its
   conftest override. Convert `alice_many_chats` to SELECT.

After step 5, `tests/fixtures/database.py` is gone (replaced by the package)
and the three per-directory conftest overrides are gone.

## Risks and mitigations

- **Template name collisions across xdist workers.** Each name carries a
  per-worker suffix derived from `worker_id`, identical to the current
  `f"test-primary_database-{uuid4()}"` pattern.
- **Stale connections blocking `CREATE DATABASE TEMPLATE`.** The chain
  builder disposes its engine after every seed step; the per-method
  `database_sessionmaker` disposes its engine on teardown. Both already
  exist today and are reused.
- **Seed determinism.** Today's `many_*` fixtures use fixed `random.seed(…)`
  values. Those seeds move into the chain seeds verbatim so the same data
  is produced. SELECT fixtures rely on deterministic IDs from the seed
  step; they sort by `id` or by `name` to be stable.
- **Test ordering inside a class.** Per-method clones make ordering
  irrelevant — the previous "first method seeds, rest read" ordering quirk
  goes away.
- **Build cost at session start.** The chain builds 12 templates
  sequentially per worker. The work is the same as today's class-scoped
  rebuilds, just front-loaded. Net wall-clock time should drop because each
  template is built once instead of once-per-class.

## Open follow-ups (not in scope)

- A `babycli db template build` operations command that materializes the
  chain in a dev environment for ad-hoc inspection.
- Cross-worker template sharing via a content hash + advisory lock, if
  per-worker build cost ever becomes the dominant cost.
