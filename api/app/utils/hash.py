import logging
from typing import Any, Self

from passlib.context import CryptContext
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

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

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        def validate(value: str | HashedStr):
            return cls(value)

        def serialize(value: HashedStr):
            return str(value)

        return core_schema.no_info_plain_validator_function(
            function=validate,
            json_schema_input_schema=core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize, when_used="json"
            ),
        )
