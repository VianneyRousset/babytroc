import asyncio

from .app import create_app
from .config import Config

config = Config.from_env()
app = asyncio.run(create_app(config))
