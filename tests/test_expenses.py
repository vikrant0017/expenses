import asyncio
from pprint import pprint

from httpx import AsyncClient


async def test_create_expense(client: AsyncClient):
    # Setup: Create Group and User directly in DB
    payload = {
        "title": "Lunch",
        "amount": "50.00",
        "group_id": 1,  # Just for experimenting
        "user_id": 1,
    }

    response = await client.post("/expenses", json=payload)
    data = response.json()
    pprint(data)


async def test_read_expenses(client: AsyncClient):
    # Create expense via API (or DB)
    payload = {
        "title": "Dinner",
        "amount": "100.00",
        "group_id": 1,
        "user_id": 1,
    }
    await client.post("/expenses", json=payload)

    response = await client.get("/expenses")
    data = response.json()
    # Note: This might return expenses from other tests if DB isn't isolated properly per test.
    # Our fixture rolls back, so it should be isolated.
    pprint(data)


async def _run_tests():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        await test_create_expense(client)
        await test_read_expenses(client)


if __name__ == "__main__":
    asyncio.run(_run_tests())
