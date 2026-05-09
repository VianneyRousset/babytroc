from dataclasses import dataclass


@dataclass(frozen=True)
class ItemCreated:
    item_id: int
    owner_id: int


@dataclass(frozen=True)
class ItemUpdated:
    item_id: int
    owner_id: int


@dataclass(frozen=True)
class ItemDeleted:
    item_id: int
    owner_id: int


@dataclass(frozen=True)
class ItemLiked:
    item_id: int
    user_id: int
    item_owner_id: int


@dataclass(frozen=True)
class ItemUnliked:
    item_id: int
    user_id: int
    item_owner_id: int


@dataclass(frozen=True)
class ItemSaved:
    item_id: int
    user_id: int


@dataclass(frozen=True)
class ItemUnsaved:
    item_id: int
    user_id: int
