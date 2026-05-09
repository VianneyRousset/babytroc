import enum

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core.core_schema import CoreSchema


class EnumWithMetadata(enum.Enum):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)

        # add names
        if "members" in core_schema:
            json_schema["x-enum-varnames"] = [e.name for e in core_schema["members"]]

        return json_schema
