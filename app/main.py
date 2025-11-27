from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import expenses, groups, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Expenses API", lifespan=lifespan)

app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(groups.router)


@app.get("/")
def root():
    return {"message": "Hello from expenses!"}


@app.get("/health")
def health():
    return {"status": "ok"}
