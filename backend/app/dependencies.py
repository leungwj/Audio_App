# Sytem imports
import os

# FastAPI-related imports
from app.postgres.postgres_db import Postgres_DB

# SQLAlchemy-related imports
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

# Security-related imports
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

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
    # Postgres_DB.create_all_tables(engine=engine, overwrite=True)

def dispose_db():
    engine.dispose()