# Compatibility shim — real module has moved to app.infrastructure.database
from app.infrastructure.database import *  # noqa: F401,F403
from app.infrastructure.database import (
    create_session_maker,
    get_db_session,
    get_session_maker,
    init_db_session_dependency,
)
