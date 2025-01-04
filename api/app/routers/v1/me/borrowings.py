from typing import Annotated

from fastapi import Query, Request, Response, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.loan.api import LoanApiQuery
from app.schemas.loan.query import LoanQueryFilter
from app.schemas.loan.read import LoanRead
from app.schemas.query import QueryPageOptions
from app.utils import set_query_param

from .me import router

# READ


@router.get("/borrowings", status_code=status.HTTP_200_OK)
def list_client_borrowings(
    request: Request,
    response: Response,
    query: Annotated[LoanApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[LoanRead]:
    """List loans where the client is the borrower."""

    client_user_id = services.auth.check_auth(request)

    result = services.loan.list_loans(
        db=db,
        query_filter=LoanQueryFilter(
            borrower_id=client_user_id,
            item_id=query.item,
            active=query.active,
        ),
        page_options=QueryPageOptions(
            limit=query.n,
            order=["loan_id"],
            cursor={"loan_id": query.cid},
            desc=True,
        ),
    )

    query_params = request.query_params
    for k, v in result.next_cursor().items():
        # rename query parameters
        k = {
            "loan_id": "cid",
        }[k]

        query_params = set_query_param(query_params, k, v)

    response.headers["Link"] = f'<{request.url.path}?{query_params}>; rel="next"'

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data
