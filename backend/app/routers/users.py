# Sytem imports
import os
from typing import Union, Annotated, Tuple, Dict, Any
from datetime import datetime, timedelta, timezone

# FastAPI-related imports
from fastapi import APIRouter, Form, status, Response, Depends, HTTPException
from app.dependencies import get_session, oauth2_scheme, pwd_context
from app.postgres.postgres_db import Postgres_DB
from app.postgres.mappings import User
from app.routers.base import BaseRouter

# SQLAlchemy-related imports
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

# token-related imports
import jwt
from jwt.exceptions import InvalidTokenError

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
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

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

        access_token_expires = timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
        acccess_token = create_access_token(
            data = {
                "sub": str(user.id)
            },
            expires_delta = access_token_expires
        )

        return Token(access_token=acccess_token, token_type="bearer")
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = str(e),
            headers = {"WWW-Authenticate": "Bearer"}
        )

@router.get("/", status_code=status.HTTP_200_OK)
async def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = decode_access_token(token)

    return await BaseRouter.retrieve(
        id=UUID(user_id),
        cls=User,
        scheme=UserScheme,
        response=None,
        session=session
    )

# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
    
#     return current_user

# @router.get("/me")
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)]
# ):
#     return current_user

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

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

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

# Token-related functions
# -----------------------

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(
    data: dict, # contains { "sub": str(user.id) }
    expires_delta: Union[timedelta, None] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("JWT_SIGNING_ALGORITHM"))
    return encoded_jwt

def decode_access_token(
    token: str
) -> User:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("JWT_SIGNING_ALGORITHM")])
        user_id: str = payload.get("sub") # sub is the subject of the token, which is the user_id
        if user_id is None:
            raise Exception("Could not validate credentials")
        
        return user_id
        
    except (Exception, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )