# Sytem imports
from typing import Union, Annotated, Tuple, Dict, Any

# FastAPI-related imports
from fastapi import APIRouter, Form, status, Response, Depends, HTTPException
from app.dependencies import get_session, oauth2_scheme, decode_access_token, create_access_token, verify_password, get_password_hash
from app.postgres.postgres_db import Postgres_DB
from app.postgres.mappings import User
from app.routers.base import BaseRouter

# SQLAlchemy-related imports
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

# Extra imports
from uuid import UUID
from sqlalchemy import or_

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

# User-related functions
# ---------------------------------------------------------------------

class UserScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: str
    full_name: str
    disabled: bool

# Invoked from main.py's /token route
async def login_for_access_token(
    username: str,
    password: str,
    session: Session,
):
    try:
        success, res = authenticate_user(username, password, session)

        if not success:
            raise Exception(res.get("error"))
        
        user: User = res.get("user")

        success, res = create_access_token(
            data = {
                "sub": str(user.id)
            }
        )

        if not success:
            raise Exception(res.get("error"))
        
        print(res)

        return res
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = str(e),
            headers = {"WWW-Authenticate": "Bearer"}
        )

@router.get("/", status_code=status.HTTP_200_OK)
async def get_current_user(
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = decode_access_token(token)

    return await BaseRouter.retrieve(
        id=UUID(user_id),
        cls=User,
        scheme=UserScheme,
        response=response,
        session=session
    )

# put wildcard routes last
@router.put("/", status_code=status.HTTP_202_ACCEPTED)
async def update_user(
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = decode_access_token(token)

    return await BaseRouter.update(
        id=UUID(user_id),
        cls=User,
        fields={
            "username": username,
            "email": email,
            "full_name": full_name,
        },
        response=response,
        session=session,
        validate=validate_user
    )

@router.delete("/", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = decode_access_token(token)

    return await BaseRouter.delete(
        id=UUID(user_id),
        cls=User,
        response=response,
        session=session
    )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
    response: Response,
    session: Annotated[Session, Depends(get_session)]
):
    return await BaseRouter.create(
        cls=User,
        fields={
            "username": username,
            "email": email,
            "password_hash": get_password_hash(password),
            "full_name": full_name,
            "disabled": False
        },
        response=response,
        session=session,
        validate=validate_user
    )

# Helper Functions
# ---------------------------------------------------------------------

# Validation Functions
# --------------------
def validate_user(session: Session, obj: User) -> Tuple[bool, Dict[str, Any]]:
    try:
        res = session.query(User).filter(
            User.id != obj.id,
            or_(
                User.email == obj.email,
                User.username == obj.username
            )
        ).all()

        if len(res) > 0:
            raise Exception("Email or username already exists!")

        return True, {
            "error": ""
        }

    except Exception as e:
        return False, {
            "error": str(e)
        }


# Authentication Functions
# ------------------------

def authenticate_user(
    username: str,
    password: str,
    session: Session
) -> Tuple[bool, Union[str, Any]]:
    try:
        success, res = Postgres_DB.retrieve(session=session, tbl=User, value=username, col_name="username")
        if not success:
            raise Exception(res.get("error"))
        elif len(res.get("objs")) == 0:
            raise Exception("Incorrect username or password")
        
        user: User = res.get("objs")[0]

        if not verify_password(password, user.password_hash):
            raise Exception("Incorrect username or password")
        
        return True, {
            "user": user
        }
    
    except Exception as e:
        return False, {
            "error": str(e)
        }