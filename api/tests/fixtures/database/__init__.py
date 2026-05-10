"""Public surface — pytest auto-discovers fixtures via pytest_plugins.

`tests/conftest.py::pytest_plugins` references this package.
"""

from tests.fixtures.database.infrastructure.admin import (
    create_database,
    drop_database,
)
from tests.fixtures.database.infrastructure.lifecycle import (
    database,
    database_sessionmaker,
    primary_database,
    primary_databases,
)

__all__ = [
    "create_database",
    "database",
    "database_sessionmaker",
    "drop_database",
    "primary_database",
    "primary_databases",
]
