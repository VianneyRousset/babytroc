#!/usr/bin/env python

import json
from tqdm import tqdm

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import time

from app import clients, models, services, schemas, config
from pprint import pprint
import random
import string


def create_extensions(conn):
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin;"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))


def create_functions(conn):
    conn.execute(
        text(
            "CREATE OR REPLACE FUNCTION normalize_text(text) RETURNS text AS $$ "
            "SELECT lower(unaccent($1)); "
            "$$ "
            "LANGUAGE SQL IMMUTABLE;"
        )
    )


def create_collations(conn):
    conn.execute(
        text(
            "CREATE COLLATION IF NOT EXISTS ignore_case_and_accent "
            "(provider = icu, locale = 'und-u-ks-level1-kc-true', "
            "deterministic = false);"
        )
    )


def randomword(length, spaces=0):
    letters = string.ascii_lowercase + " " * spaces
    return "".join(random.choice(letters) for i in range(length))


def load_data(db):
    with open("data.json") as f:
        data = json.load(f)

    # create regions
    for region in data["regions"]:
        services.region.create_region(
            db=db,
            region_create=schemas.region.create.RegionCreate(**region),
        )

    # create users
    for user in data["users"]:
        services.user.create_user(
            db=db,
            user_create=schemas.user.create.UserCreate(**user),
        )

    # create images
    for item in tqdm(data["items"]):
        for image_name in item["images"]:
            clients.database.image.create_image(
                db=db,
                name=image_name,
                owner_id=item["owner_id"],
            )

    # create items
    for item in tqdm(data["items"]):
        owner_id = item.pop("owner_id")
        services.item.create_item(
            db=db,
            owner_id=owner_id,
            item_create=schemas.item.create.ItemCreate(**item),
        )


def main():
    engine = create_engine(config.DATABASE_URL)
    session_maker = sessionmaker(bind=engine, autoflush=False)

    with engine.begin() as conn:
        # prepare database (install extensions and create tables)
        create_extensions(conn)
        create_functions(conn)
        # create_collations(conn)
        models.base.Base.metadata.drop_all(conn)
        models.base.Base.metadata.create_all(conn)

    with session_maker() as db:
        with db.begin():
            load_data(db)

    # save an item
    with session_maker() as db:
        with db.begin():
            services.item.save.add_item_to_user_saved_items(
                db=db,
                user_id=1,
                item_id=42,
            )

    print("*" * 80)

    # like an item
    with session_maker() as db:
        with db.begin():
            services.item.like.add_item_to_user_liked_items(
                db=db,
                user_id=1,
                item_id=3,
            )

    print("*" * 80)

    # create loan request, accept it and execute it
    with session_maker() as db:
        with db.begin():
            # create loan request
            loan_request = services.loan.create_loan_request(
                db=db,
                borrower_id=2,
                item_id=49,
            )

            pprint(loan_request.model_dump())
            print("*" * 80)

            return

            # accept loan request
            loan_request = services.loan.accept_loan_request(
                db=db,
                loan_request_id=loan_request.id,
            )

            pprint(loan_request.model_dump())
            print("*" * 80)

            # execute loan request
            loan = services.loan.execute_loan_request(
                db=db,
                loan_request_id=loan_request.id,
            )

            pprint(loan_request.model_dump())
            print("*" * 80)

    return

    with session_maker() as db:
        with db.begin():
            messages = services.chat.list_messages(
                db=db,
                query_filter=schemas.chat.query.ChatMessageQueryFilter(
                    member_id=1,
                ),
            )
            pprint(messages.model_dump())
            print("*" * 80)


if __name__ == "__main__":
    main()
