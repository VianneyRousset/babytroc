from typing import TYPE_CHECKING, Annotated

from fastapi import Body, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item import services as item_services
from babytroc.domains.item.schemas.create import ItemCreate
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import client_id_annotation
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config


class ItemCreateRequest(AntiBotMixin, ItemCreate):
    pass


rate_limit_item_create = make_rate_limit_dep(
    key_prefix="item_create",
    extract_config=lambda c: c.item_create,
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_client_item(
    client_id: client_id_annotation,
    item_create_request: Annotated[
        ItemCreateRequest,
        Body(title="Fields for the item creation."),
    ],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    _rate_limited: Annotated[None, Depends(rate_limit_item_create)],
) -> ItemRead:
    """Create an item owned by the client."""

    config: Config = request.app.state.config
    await verify_antibot(item_create_request, config.cap)

    item_create = ItemCreate(
        name=item_create_request.name,
        description=item_create_request.description,
        images=item_create_request.images,
        targeted_age_months=item_create_request.targeted_age_months,
        regions=item_create_request.regions,
        blocked=item_create_request.blocked,
        categories=item_create_request.categories,
    )

    return await item_services.create_item(
        db=db,
        owner_id=client_id,
        item_create=item_create,
    )
