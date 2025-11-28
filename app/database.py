import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()
# Database URL
# Assuming postgres user/password from compose.yaml and default port 5432
PG_HOST = os.getenv("PG_HOST", "postgres")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
PG_DB = os.getenv("PG_DB", "postgres")
PG_PORT = os.getenv("PG_PORT", "5432")

DEBUG_SQL = os.getenv("DEBUG_SQL", False)

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(DATABASE_URL, echo=bool(DEBUG_SQL))


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
