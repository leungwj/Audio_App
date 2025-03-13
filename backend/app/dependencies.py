# Sytem imports
import os
from datetime import datetime, timedelta, timezone
from typing import Union

# FastAPI-related imports
from app.postgres.postgres_db import Postgres_DB
from fastapi import HTTPException, status
from app.postgres.mappings import User

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
    try:
        success = Postgres_DB.test_connection(engine=engine)

        if not success:
            raise Exception("Could not connect to the database")

        success = Postgres_DB.create_all_tables(engine=engine)

        if not success:
            raise Exception("Could not create tables")
        
        success = create_default_user(engine=engine)

        if not success:
            raise Exception("Could not create default user")

    except Exception as e:
        print(f"[!] (FastAPI) Fatal Error: {e}")

def dispose_db():
    engine.dispose()

@staticmethod
def create_default_user(engine: Engine) -> bool:

    with Session(engine) as session:
        try:
            success, res = Postgres_DB.retrieve(session=session, tbl=User, value="admin", col_name="username")

            if not success:
                raise Exception(res.get("error"))
            elif len(res.get("objs")) > 0: # user already exists
                return True

            user = User(
                username="admin",
                email="admin@gmail.com",
                password_hash=get_password_hash("admin"),
                full_name="Administrator"
            )

            success, res = Postgres_DB.insert(session=session, obj=user)

            if not success:
                raise Exception(res.get("error"))
            
            return True
    
        except Exception as e:
            print(f"[!] (Postgres) Failed to create default user: {e}")
            return False

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
    
# Auth-related functions
# -----------------------

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)