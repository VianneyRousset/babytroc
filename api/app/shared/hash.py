from typing import Any, Self

import bcrypt
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class HashedStr(str):
    def __new__(cls, o: str | Self | None = None, *, hashed: str | Self | None = None):
        # use hashed string
        if o is None:
            if hashed is None:
                msg = "Missing input value"
                raise ValueError(msg)

            if not isinstance(hashed, str):
                msg = f"Type of hashed is expected to be str, got {type(hashed)}"
                raise TypeError(msg)

            return str.__new__(HashedStr, hashed)

        # already hashed
        if isinstance(o, HashedStr):
            return str.__new__(HashedStr, o)

        # to be hashed
        if isinstance(o, str):
            return str.__new__(
                HashedStr,
                bcrypt.hashpw(
                    o.encode("utf-8"),
                    bcrypt.gensalt(),
                ).decode("utf-8"),
            )

        msg = f"HashedStr or str is expected, got {type(o)}"
        raise TypeError(msg)

    def verify(self, plain: str):
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            self.encode("utf-8"),
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        def validate(value: str | HashedStr):
            return cls(value)

        return core_schema.no_info_plain_validator_function(
            function=validate,
            json_schema_input_schema=core_schema.str_schema(),
        )

    def __repr__(self) -> str:
        return f"HashedStr({str(self)!r})"
