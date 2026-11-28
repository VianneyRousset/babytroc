from pydantic import EmailStr

from babytroc.shared.schemas import ReadBase


class ModerationPrivilegeRead(ReadBase):
    user_id: int
    name: str
    email: EmailStr
    moderator: bool
    admin: bool
