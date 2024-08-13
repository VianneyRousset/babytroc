from datetime import datetime

from .base import Base


class User(Base):
    id: int
    name: str
    creation_date: datetime


class PrivateUser(User):
    email: str
    password: str


class UserCreation(Base):
    email: str
    password: str
