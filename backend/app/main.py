from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.dependencies import initialise_db, dispose_db
from app.routers import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[*] (FastAPI) Initialising...")
    initialise_db()
    # ---------------------------------------
    # Before server starts, run code above

    yield

    # Before server stops, run code below
    # ---------------------------------------
    print("[*] (FastAPI) Shutting down...")
    dispose_db()

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}