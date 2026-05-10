"""@pytest.mark.db_template marker reader."""

import pytest

from tests.fixtures.database.infrastructure.registry import (
    DEFAULT_TEMPLATE,
    TEMPLATES,
)

MARKER_NAME = "db_template"


def get_template_name(request: pytest.FixtureRequest) -> str:
    """Return the template name declared by `@pytest.mark.db_template("…")`.

    Looks at the closest marker (function → class → module). Defaults to
    DEFAULT_TEMPLATE if no marker is set.
    """
    marker = request.node.get_closest_marker(MARKER_NAME)
    if marker is None:
        return DEFAULT_TEMPLATE

    if not marker.args:
        msg = f"@pytest.mark.{MARKER_NAME}(...) requires a template name argument"
        raise ValueError(msg)

    name = marker.args[0]
    if name not in TEMPLATES:
        valid = ", ".join(sorted(TEMPLATES))
        msg = f"Unknown db_template {name!r}. Valid: {valid}"
        raise ValueError(msg)

    return name
