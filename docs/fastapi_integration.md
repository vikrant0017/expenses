# FastAPI and SQLAlchemy Integration

This document explains how FastAPI is integrated with SQLAlchemy in this application.

## Pattern Overview

We use the **Dependency Injection** pattern provided by FastAPI to manage database sessions. This ensures that a new database session is created for each request and closed after the request is processed.

### 1. Database Setup (`app/database.py`)

- **`AsyncSessionLocal`**: A session factory configured to create `AsyncSession` instances.
- **`get_db`**: An asynchronous generator function.
    - It creates a session: `async with AsyncSessionLocal() as session:`.
    - It `yields` the session to the path operation.
    - It automatically closes the session when the request is done (handled by the context manager).

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

### 2. Dependency Injection in Routers

In your path operations (endpoints), you declare a parameter of type `AsyncSession` and use `Depends(get_db)`. FastAPI handles the rest.

```python
@router.post("/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Use 'db' session here
    ...
```

### 3. Pydantic vs SQLAlchemy Models

- **SQLAlchemy Models (`app/models.py`)**: Represent the database tables. Used for DB interactions.
- **Pydantic Models (`app/schemas.py`)**: Represent the API request and response bodies. Used for validation and serialization.

**Data Flow:**
1.  **Request**: JSON -> Pydantic Model (`UserCreate`)
2.  **Logic**: Pydantic Model -> SQLAlchemy Model (`User`) -> Database
3.  **Response**: Database -> SQLAlchemy Model -> Pydantic Model (`UserRead`) -> JSON

## Async Considerations

- We use `asyncpg` driver for asynchronous database access.
- All DB operations must be awaited (e.g., `await db.execute(...)`, `await db.commit()`).
- `AsyncSession` is used instead of the standard `Session`.
