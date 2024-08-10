from fastapi import FastAPI, Request
from pydantic import BaseModel

from routers.items import router as router_items
from routers.users import router as router_users

import db

app = FastAPI()

app.include_router(router_users)
app.include_router(router_items)


class Login(BaseModel):
    user: db.users.User


@app.get("/login")
async def login(request: Request) -> Login:
    return Login(
        user=db.users.alice,
    )
