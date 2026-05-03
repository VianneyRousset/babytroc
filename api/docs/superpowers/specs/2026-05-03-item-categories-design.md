# Item Categories Design

## Overview

Add nested categories (max 2 levels) to items. Items can belong to multiple categories. Filtering by a parent category includes all descendants.

## Data Model

### `category` table

| Column       | Type              | Constraints                          |
|-------------|-------------------|--------------------------------------|
| `slug`       | `String`          | PK, unique, indexed                  |
| `name`       | `String`          | Not null (French display name)       |
| `parent_slug`| `String` or NULL  | FK to `category.slug`, nullable      |

Parent categories have `parent_slug = NULL`. Children reference their parent. Max depth enforced by convention (no child can have a parent that itself has a parent).

### `item_category_association` table

| Column          | Type      | Constraints                     |
|----------------|-----------|----------------------------------|
| `item_id`       | `Integer` | FK to `item.id`, PK, CASCADE    |
| `category_slug` | `String`  | FK to `category.slug`, PK, CASCADE |

### Item model changes

New relationship `categories` via `item_category_association`, same pattern as `regions`.

## API

### `GET /api/v1/categories`

Returns all categories as a flat list. No auth required.

Response: `list[CategoryRead]`

### Item filtering

New query param on `/api/v1/items` (and related item list endpoints):
- Alias: `cat`
- Type: `list[str] | None`
- Behavior: item matches if any of its categories has `slug IN (:slugs) OR parent_slug IN (:slugs)`

This means filtering by `clothing` returns items tagged `clothing`, `clothing-bodysuits`, `clothing-sleepwear`, etc.

## Schemas

### `CategoryRead`

```python
slug: str
name: str
parent_slug: str | None
```

### `ItemRead` changes

Add `categories: list[CategoryRead]`.

## Query Filter

New `ItemQueryFilterCategories` mixin class following the `ItemQueryFilterRegions` pattern. Plugged into `ItemReadQueryFilter` (and update/delete filters as needed).

Filter logic: join `item_category_association` + `category`, where `category.slug IN (slugs) OR category.parent_slug IN (slugs)`.

## Seed Data

French names, English slugs:

| Parent slug   | Parent name   | Child slug             | Child name          |
|--------------|---------------|------------------------|---------------------|
| `clothing`    | Vetements     | `clothing-bodysuits`   | Bodies              |
|              |               | `clothing-sleepwear`   | Pyjamas             |
|              |               | `clothing-outerwear`   | Manteaux            |
|              |               | `clothing-accessories` | Accessoires         |
| `toys`        | Jouets        | `toys-bath`            | Jouets de bain      |
|              |               | `toys-soft`            | Peluches            |
|              |               | `toys-educational`     | Jouets educatifs    |
| `gear`        | Equipement    | `gear-strollers`       | Poussettes          |
|              |               | `gear-car-seats`       | Sieges auto         |
|              |               | `gear-carriers`        | Porte-bebes         |
| `furniture`   | Mobilier      | `furniture-cribs`      | Lits                |
|              |               | `furniture-chairs`     | Chaises             |
|              |               | `furniture-changing`   | Tables a langer     |
| `feeding`     | Repas         | `feeding-bottles`      | Biberons            |
|              |               | `feeding-bibs`         | Bavoirs             |
|              |               | `feeding-highchairs`   | Chaises hautes      |
| `hygiene`     | Hygiene       | `hygiene-diapers`      | Couches             |
|              |               | `hygiene-bath`         | Bain                |
|              |               | `hygiene-care`         | Soins               |

Seed assigns 1-3 random categories per item.

## Testing

- `GET /api/v1/categories` returns full category list
- `/api/v1/items?cat=clothing` returns items tagged with `clothing` or any child (`clothing-bodysuits`, etc.)
- `/api/v1/items?cat=clothing-bodysuits` returns only items tagged exactly with `clothing-bodysuits`
- `/api/v1/items?cat=clothing&cat=toys` returns items in either family

## Migration

New Alembic migration adding `category` table, `item_category_association` table.
