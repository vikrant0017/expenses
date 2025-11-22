from fastapi import FastAPI
from app.routers import users, expenses

app = FastAPI(title="Expenses API")

app.include_router(users.router)
app.include_router(expenses.router)

@app.get("/")
async def root():
    return {"message": "Hello from expenses!"}

@app.get("/health")
async def health():
    return {"status": "ok"}
