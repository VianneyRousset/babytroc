from .app import create_app
from .config import Config

config = Config.from_env()
app = create_app(config)
