from babytroc.domains.auth.events import AccountValidated
from babytroc.domains.item.events import ItemCreated
from babytroc.infrastructure.events import on


@on(ItemCreated)
async def award_stars_on_item_created(db, event: ItemCreated):
    from babytroc.domains.user.services.star.update import AddUserStars, add_many_stars_to_users
    from babytroc.domains.user.star import stars_gain_when_adding_item

    await add_many_stars_to_users(
        db=db,
        stars=[
            AddUserStars(
                user_id=event.owner_id,
                stars_count=stars_gain_when_adding_item(1),
            )
        ],
    )


@on(AccountValidated, critical=False)
async def invalidate_user_cache_on_validation(db, event: AccountValidated):
    from babytroc.infrastructure.cache import get_cache
    from babytroc.domains.user.services.cache import invalidate_user_validated

    cache = get_cache()
    await invalidate_user_validated(cache, user_id=event.user_id)
