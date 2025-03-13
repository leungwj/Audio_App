# Sytem imports
import os
from datetime import datetime, timedelta, timezone
from typing import Union

# FastAPI-related imports
from app.postgres.postgres_db import Postgres_DB
from fastapi import HTTPException, status

# SQLAlchemy-related imports
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

# Security-related imports
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

# token-related imports
import jwt
from jwt.exceptions import InvalidTokenError

engine: Engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DATABASE')}",
    isolation_level="SERIALIZABLE"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_session():
    with Session(engine) as session:
        yield session

def initialise_db():
    result = Postgres_DB.test_connection(engine=engine)
    # db.drop_all_tables()
    # TODO: Only run this if the tables don't exist
    # TODO: Seed a default user if the users table is empty
    # Postgres_DB.create_all_tables(engine=engine, overwrite=True)

def dispose_db():
    engine.dispose()


# Token-related functions
# -----------------------

def create_access_token(
    data: dict, # contains { "sub": str(user.id) }
    expires_delta: Union[timedelta, None] = None
):
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
        
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("JWT_SIGNING_ALGORITHM"))

        # do not change this format, it is the format expected by the OAuth2
        return True, { "access_token": encoded_jwt, "token_type": "bearer" }
    except Exception as e:
        return False, { 
            "error": str(e)
        }

def decode_access_token(
    token: str
):
    try:
        # will raise an exception if the token is invalid, or if the token is expired
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