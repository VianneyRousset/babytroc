# Compatibility shim — real module has moved to app.infrastructure.pubsub
from app.infrastructure.pubsub import *  # noqa: F401,F403
from app.infrastructure.pubsub import (
    flush_pending_notifications,
    get_broadcast,
    init_broadcast_dependency,
    notify_user,
    notify_user_after_commit,
    user_channel,
)
