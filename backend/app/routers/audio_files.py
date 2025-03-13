# Sytem imports
from typing import Union, Annotated, Tuple, Dict, Any

# FastAPI-related imports
from fastapi import APIRouter, Form, status, Response, Depends, HTTPException
from app.dependencies import get_session, oauth2_scheme
from app.postgres.postgres_db import Postgres_DB
from app.postgres.mappings import Audio_File
from app.routers.base import BaseRouter

# SQLAlchemy-related imports
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

# Extra imports
from uuid import UUID
from sqlalchemy import and_

router = APIRouter(
    prefix="/audio_files",
    tags=["audio_files"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def read_root(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    return {"token": token}