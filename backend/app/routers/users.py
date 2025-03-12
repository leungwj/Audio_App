# Sytem imports
from typing import Union, Annotated, Tuple, Dict, Any

# FastAPI-related imports
from fastapi import APIRouter, Form, status, Response, Depends, HTTPException
from app.dependencies import get_session
from app.postgres.postgres_db import Postgres_DB
from app.postgres.mappings import User
from app.routers.base import BaseRouter

# SQLAlchemy-related imports
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

# Extra imports
from uuid import UUID
from sqlalchemy import and_

class UserScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    # password_hash: str
    first_name: str
    last_name: str
    role: str

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}}
)

# put wildcard routes last
@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    id: UUID,
    email: Annotated[str, Form()],
    password_hash: Annotated[str, Form()],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    role: Annotated[str, Form()],
    response: Response,
    session: Annotated[Session, Depends(get_session)]
):
    return await BaseRouter.update(
        id=id,
        cls=User,
        fields={
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "role": role
        },
        response=response,
        session=session,
        validate=validate_email
    )

@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(
    id: UUID,
    password_hash: Annotated[str, Form()],
    response: Response,
    session: Annotated[Session, Depends(get_session)]
):
    return await BaseRouter.delete(
        id=id,
        cls=User,
        response=response,
        session=session
    )

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def retrieve_user(
    id: UUID,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    session_id: Union[str, None] = None,
):
    return await BaseRouter.retrieve(
        id=id,
        cls=User,
        scheme=UserScheme,
        response=response,
        session=session
    )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    email: Annotated[str, Form()],
    password_hash: Annotated[str, Form()],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    role: Annotated[str, Form()],
    response: Response,
    session: Annotated[Session, Depends(get_session)]
):
    return await BaseRouter.create(
        cls=User,
        fields={
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "role": role
        },
        response=response,
        session=session,
        validate=validate_email
    )

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    email: Annotated[str, Form()],
    password_hash: Annotated[str, Form()],
    response: Response,
    session: Annotated[Session, Depends(get_session)]
):
    try:
        success, res = Postgres_DB.retrieve(session=session, tbl=User, value=email)

        if not success:
            raise Exception(res.get("error"))
        elif len(res.get("objs")) == 0:
            raise Exception(f"Invalid credentials!")

        user: User = res.get("objs")[0]

        if not user.authenticate(input_pwd_hash=password_hash):
            raise Exception("Invalid credentials!")

        return {
            "session_id": user.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
            detail=str(e)
        )

# Helper Functions
# ---------------------------------------------------------------------

def validate_email(session: Session, obj: User) -> Tuple[bool, Dict[str, Any]]:
    try:
        res = session.query(User).filter(
            User.id != obj.id,
            and_(
                User.email == obj.email,
            )
        ).all()

        if len(res) > 0:
            raise Exception("Email already exists!")

        return True, {
            "error": ""
        }

    except Exception as e:
        return False, {
            "error": str(e)
        }