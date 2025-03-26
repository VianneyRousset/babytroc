import enum

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class EnumWithMetadata(enum.Enum):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)

        # add names
        json_schema["x-enum-varnames"] = [e.name for e in core_schema["members"]]

        return json_schema


class ChatMessageType(int, EnumWithMetadata):
    text = 1
    loan_request_created = 2
    loan_request_cancelled = 3
    loan_request_accepted = 4
    loan_request_rejected = 5
    loan_started = 6
    loan_ended = 7
    item_not_available = 8
    item_available = 9


class ReportType(int, EnumWithMetadata):
    user = 1
    item = 2
    chat = 3


class LoanRequestState(int, EnumWithMetadata):
    pending = 1
    cancelled = 2
    accepted = 3
    rejected = 4
    executed = 5


class ItemQueryAvailability(str, EnumWithMetadata):
    yes = "y"
    no = "n"
    all = "a"
