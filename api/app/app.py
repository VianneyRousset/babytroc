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

from app.errors import ApiError

from .config import Config
from .database import create_async_session_maker, create_session_maker
from .routers.v1 import router


# TODO check usefull ?
@asynccontextmanager
async def lifespan(app: FastAPI):
    await app.state.broadcast.connect()
    yield
    await app.state.broadcast.disconnect()


class DelayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        await asyncio.sleep(request.app.state.config.delay)
        return await call_next(request)


def create_app(config: Config) -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        root_path="/api",
    )

    app.state.config = config
    app.state.db_async_session_maker = create_async_session_maker(
        config.database.async_url
    )

    # database session maker
    app.state.db_session_maker = create_session_maker(config.database.url)

    # broadcaster
    app.state.broadcast = Broadcast(
        config.pubsub.url.render_as_string(hide_password=False)
    )

    # email_client
    app.state.email_client = FastMail(
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

    return app
