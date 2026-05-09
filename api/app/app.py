import asyncio
from contextlib import asynccontextmanager

from broadcaster import Broadcast
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig as EmailConnectionConfig
from fastapi_mail import FastMail
from pydantic import SecretStr
from starlette.middleware.base import BaseHTTPMiddleware

import app.domains  # noqa: F401 — registers all domain models with SQLAlchemy metadata
from app.shared.errors import ApiError

from .infrastructure.cache import init_cache_dependency
from .infrastructure.cache_client import RedisCache
from .infrastructure.config import Config
from .infrastructure.database import create_session_maker, init_db_session_dependency
from .infrastructure.email import init_email_dependency
from .infrastructure.pubsub import init_broadcast_dependency
from .infrastructure.redis import create_redis_client
from .routers.v1 import router


# TODO check usefull ?
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with app.state.broadcast:
        yield
    await app.state.redis.aclose()


class RootPathMiddleware:
    """Strip root_path prefix from request path."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            root_path = scope.get("root_path", "")
            path = scope.get("path", "")
            if root_path and path.startswith(root_path):
                scope = dict(scope, path=path[len(root_path):] or "/")
        await self.app(scope, receive, send)


class DelayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        await asyncio.sleep(request.app.state.config.delay)
        return await call_next(request)


def create_app(
    config: Config | None = None,
    *,
    pubsub_channel_prefix: str = "",
) -> FastAPI:
    if config is None:
        config = Config.from_env()

    app = FastAPI(
        lifespan=lifespan,
    )

    app.state.config = config

    # database session maker
    pool_kwargs: dict = {}
    if config.test:
        from sqlalchemy.pool import NullPool

        pool_kwargs["poolclass"] = NullPool
    else:
        pool_kwargs["pool_size"] = 10
        pool_kwargs["max_overflow"] = 20
        pool_kwargs["pool_pre_ping"] = True
        pool_kwargs["pool_recycle"] = 1800
    db_session_maker = create_session_maker(config.database.url, **pool_kwargs)
    app.state.db_session_maker = db_session_maker
    init_db_session_dependency(db_session_maker)

    # broadcaster
    broadcast = Broadcast(config.pubsub.url)
    app.state.broadcast = broadcast
    init_broadcast_dependency(broadcast, channel_prefix=pubsub_channel_prefix)

    # redis client and cache
    redis_client = create_redis_client(config.redis)
    app.state.redis = redis_client
    cache = RedisCache(redis_client)
    app.state.cache = cache
    init_cache_dependency(cache)

    # email_client
    email_client = FastMail(
        EmailConnectionConfig(
            MAIL_USERNAME=config.email.username,
            MAIL_PASSWORD=SecretStr(config.email.password),
            MAIL_PORT=config.email.port,
            MAIL_SERVER=config.email.server,
            MAIL_FROM=config.email.from_email,
            MAIL_FROM_NAME=config.email.from_name,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            SUPPRESS_SEND=1 if config.test else 0,
        )
    )
    app.state.email_client = email_client
    init_email_dependency(email_client)

    # add delay middleware
    if config.delay > 0:
        app.add_middleware(DelayMiddleware)

    @app.get("/")
    def root(request: Request) -> JSONResponse:
        return JSONResponse(
            status_code=200,
            content={"status": "ok"},
        )

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        # TODO extract error message
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ApiError)
    def api_exception_handler(request: Request, error: ApiError):
        return JSONResponse(
            status_code=error.status_code,
            headers=error.headers,
            content={
                "status_code": error.status_code,
                "message": error.message,
                "creation_date": error.creation_date.isoformat(),
            },
        )

    app.include_router(
        router=router,
        prefix="/v1",
    )

    app.add_middleware(RootPathMiddleware)

    return app
