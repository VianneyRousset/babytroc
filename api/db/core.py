from .models import Base
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()
