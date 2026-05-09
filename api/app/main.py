import app.domains  # noqa: F401 — registers all domain models with SQLAlchemy metadata

from .app import create_app
from .infrastructure.config import Config

config = Config.from_env()
application = create_app(config)
