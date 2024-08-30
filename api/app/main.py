from . import config
from .app import create_app

app = create_app(
    db_url=config.DATABASE_URL,
)
