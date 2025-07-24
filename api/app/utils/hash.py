import logging
from typing import Self

from passlib.context import CryptContext

# silent passlib warning "module 'bcrypt' has no attribute '__about__'"
# https://github.com/pyca/bcrypt/issues/684
logging.getLogger("passlib").setLevel(logging.ERROR)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashedStr(str):
    def __new__(cls, o: str | Self, *, hash: bool = True):
        # already hashed
        if isinstance(o, HashedStr) or (not hash and isinstance(o, str)):
            return str.__new__(HashedStr, o)

        # to be hashed
        if isinstance(o, str):
            return str.__new__(HashedStr, pwd_context.hash(o))

        msg = f"HashedStr or str is expected, got {type(o)}"
        raise TypeError(msg)

    def verify(self, plain: str):
        return pwd_context.verify(plain, self)
