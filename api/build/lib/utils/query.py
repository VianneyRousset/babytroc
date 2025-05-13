from typing import Any

from fastapi.datastructures import QueryParams


def set_query_param(query: QueryParams, key: Any, value: Any) -> QueryParams:
    key = str(key)

    # remove param
    items = [(k, v) for k, v in query.multi_items() if k != key]

    # append param
    return QueryParams([*items, (key, value)])
