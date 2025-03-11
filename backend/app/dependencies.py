# Sytem imports
import os

# FastAPI-related imports
from app.postgres.postgres_db import Postgres_DB

# SQLAlchemy-related imports
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

engine: Engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DATABASE')}",
    isolation_level="SERIALIZABLE"
)

def get_session():
    with Session(engine) as session:
        yield session

def initialise_db():
    result = Postgres_DB.test_connection(engine=engine)
    # db.drop_all_tables()
    # Snowflake_DB.create_all_tables(engine=engine, overwrite=False)

def dispose_db():
    engine.dispose()