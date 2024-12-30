import warnings

import sqlalchemy.exc
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# make sqlalchemy warnings as errors
warnings.simplefilter("error", sqlalchemy.exc.SAWarning)


def create_session_maker(db_url: str) -> sessionmaker:
    engine = create_engine(db_url, echo=False)

    return sessionmaker(
        bind=engine,
    )


# TODO switch to connections pool ?
def get_db_session(request: Request) -> Session:
    with request.app.state.db_session_maker.begin() as session:
        yield session
