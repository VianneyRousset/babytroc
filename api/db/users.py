from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    creation_date: datetime


class PrivateUser(User):
    email: str
    password: str


alice = User(
    id=0,
    name="Alice",
    creation_date=datetime.now(),
)

bob = User(
    id=1,
    name="Bob",
    creation_date=datetime.now(),
)


def get_private_user_by_email(email: str) -> PrivateUser:
    return User(
        **alice.__dict__,
        email="alice@kindbaby.ch",
        password="xxx",
    )
