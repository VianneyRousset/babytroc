from typing import Annotated, TypeVar, cast

from fastapi import Request, Response
from fastapi.datastructures import QueryParams
from pydantic import Field

from .base import Base


class QueryPageBase(Base):
    pass


class QueryPageCursor(QueryPageBase):
    """Page cursor."""

    def query_params_from_request(self, request: Request) -> QueryParams:
        """Return a merge of the request query params and the cursor."""

        return QueryParams(
            [
                *(
                    (k, v)
                    for k, v in request.query_params.multi_items()
                    if k not in self.model_fields_set
                ),
                *self.model_dump().items(),
            ]
        )

    def header_link_from_request(
        self,
        request: Request,
        rel: str,
    ) -> str:
        """Return header link header."""

        query_params = self.query_params_from_request(request)

        return f'<{request.url.path}?{query_params}>; rel="{rel}"'


QueryPageCursorT = TypeVar("QueryPageCursorT", bound=QueryPageCursor)
QueryPageDataT = TypeVar("QueryPageDataT")


class QueryPageOptions[QueryPageCursorT](QueryPageBase):
    """Options on the queried page."""

    limit: Annotated[int | None, Field(gt=0)] = None
    cursor: QueryPageCursorT


class QueryPageResult[QueryPageDataT, QueryPageCursorT](
    QueryPageBase,
    arbitrary_types_allowed=True,
):
    """Info on the result page."""

    data: list[QueryPageDataT]
    next_page_cursor: QueryPageCursorT

    @property
    def total_count(self):
        return len(self.data)

    def set_response_headers(
        self,
        response: Response,
        request: Request,
    ) -> None:
        cursor = cast("QueryPageCursor", self.next_page_cursor)
        response.headers["Link"] = cursor.header_link_from_request(request, "next")
        response.headers["X-Total-Count"] = str(self.total_count)
