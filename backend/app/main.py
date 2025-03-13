from typing import Annotated
from fastapi import FastAPI, Depends, Response
from contextlib import asynccontextmanager
from app.dependencies import initialise_db, dispose_db, get_session
from app.routers import users, audio_files
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

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
app.include_router(audio_files.router)

@app.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):
    return await users.login_for_access_token(username=form_data.username, password=form_data.password, session=session)

@app.get("/")
def read_root():
    return {"Hello": "World"}