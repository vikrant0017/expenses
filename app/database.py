from sqlmodel import create_engine, Session, SQLModel

# Database URL
# Assuming postgres user/password from compose.yaml and default port 5432
DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
