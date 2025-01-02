from .config import Config
from .app import create_app

config = Config.from_env()
app = create_app(config)
