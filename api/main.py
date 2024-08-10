from fastapi import FastAPI
# from routers.user import router as router_user
# from routers.item import router as router_item

app = FastAPI()

# app.include_router(router_user)
# app.include_router(router_item)


@app.get("/")
async def root():
    return {"message": "Hello"}
