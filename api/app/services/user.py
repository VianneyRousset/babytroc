from app.models.user import User as UserDB
from app.schemas.user import User, UserCreation
from sqlalchemy.orm import Session


async def create_user(
    session: Session,
    user: UserCreation,
) -> User:
    user = UserDB(**user.model_dump(exclude_node=True))
    session.add(user)
    session.commit()
    session.refresh()
    return User(**user.__dict__)


async def login(
    session: Session,
    email: str,
) -> User:
    user = session.query(UserDB).filter(UserDB.email == email).one()

    return User(**user.__dict__)
