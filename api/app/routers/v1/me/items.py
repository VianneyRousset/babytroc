from datetime import datetime
from typing import Annotated, Optional

from fastapi import Body, Path, Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item import ItemCreate, ItemPreviewRead, ItemRead, ItemUpdate
from app.schemas.loans import LoanRequestRead

from .me import router

item_id_annotation = (
    Annotated[
        int,
        Path(
            title="The ID of the item.",
            ge=0,
        ),
    ],
)

loan_request_id_annotation = (
    Annotated[
        int,
        Path(
            title="The ID of the loan request.",
            ge=0,
        ),
    ],
)


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_client_item(
    request: Request,
    item_create: Annotated[
        ItemCreate,
        Body(title="Fields for the item creation."),
    ],
    db: Session = Depends(get_db_session),
) -> ItemPreviewRead:
    """Create an item owned by the client."""

    client_user_id = services.auth.check_auth(request)

    return services.items.create_item(
        db=db,
        owner_user_id=client_user_id,
        item_create=item_create,
    )


@router.get("/items", status_code=status.HTTP_200_OK)
async def list_client_items(
    request: Request,
    before: Annotated[
        Optional[int],
        Query(
            title="Select item with creation date before the item with this id",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        Query(
            title="Maximum number of items to return",
            ge=0,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> list[ItemPreviewRead]:
    """List items owned by the client ordered by inversed creation date."""

    client_user_id = services.auth.check_auth(request)

    return await services.items.list_user_items(
        db=db,
        owner_user_id=client_user_id,
        created_before_item_id=before,
        count=count,
    )


@router.get("/items/{item_id}", status_code=status.HTTP_200_OK)
async def get_client_item_by_id(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Get client's item by id."""

    client_user_id = services.auth.check_auth(request)

    return await services.items.get_user_item_by_id(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
    )


@router.post("/items/{item_id}", status_code=status.HTTP_200_OK)
async def update_client_item(
    request: Request,
    item_id: item_id_annotation,
    item_update: Annotated[
        ItemUpdate,
        Body(title="Item fields to update."),
    ],
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Update client's item."""

    client_user_id = services.auth.check_auth(request)

    return await services.items.update_user_item(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
        item_update=item_update,
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_client_item(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Delete the specified item owned by the client."""

    client_user_id = services.auth.check_auth(request)

    return services.items.delete_user_item(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
    )


@router.get("/items/{item_id}/requests", status_code=status.HTTP_200_OK)
async def list_client_item_loan_requests(
    request: Request,
    item_id: item_id_annotation,
    active: Annotated[
        Optional[bool],
        Query(title="Select only active requests"),
    ] = True,
    before: Annotated[
        Optional[datetime],
        Query(
            title="Select requests with creation date strictly before this date",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        Query(
            title="Maximum number of items to return",
            ge=0,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> list[LoanRequestRead]:
    """List loan requests made for the client's item ordered by inversed start date."""

    client_user_id = services.auth.check_auth(request)

    return await services.loans.list_user_item_loan_requests(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
        active=active,
        started_before_loan_request_id=before,
        count=count,
    )


@router.get(
    "/items/{item_id}/requests/{loan_request_id}",
    status_code=status.HTTP_200_OK,
)
async def get_client_item_loan_request_by_id(
    request: Request,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Get client's item loan request by id."""

    client_user_id = services.auth.check_auth(request)

    return await services.loan.get_user_item_loan_request_by_id(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
        loan_request_id=loan_request_id,
    )


@router.post(
    "/items/{item_id}/requests/{loan_request_id}/accept",
    status_code=status.HTTP_200_OK,
)
async def accept_client_item_loan_request(
    request: Request,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Accept client's item loan request."""

    client_user_id = services.auth.check_auth(request)

    return await services.loan.accept_user_item_loan_request(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
        loan_request_id=loan_request_id,
    )


@router.post(
    "/items/{item_id}/requests/{loan_request_id}/reject",
    status_code=status.HTTP_200_OK,
)
async def reject_client_item_loan_request(
    request: Request,
    item_id: item_id_annotation,
    loan_request_id: loan_request_id_annotation,
    db: Session = Depends(get_db_session),
) -> LoanRequestRead:
    """Reject client's item loan request."""

    client_user_id = services.auth.check_auth(request)

    return await services.loan.reject_user_item_loan_request(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
        loan_request_id=loan_request_id,
    )
