import asyncio

from httpx import AsyncClient


async def test_create_user(client: AsyncClient):
    response = await client.post("/users", json={"name": "Test User"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert "id" in data


async def test_read_users(client: AsyncClient):
    # Create a user first
    await client.post("/users", json={"name": "User Man"})
    await client.post("/users", json={"name": "User Woman"})

    response = await client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [u["name"] for u in data]
    assert "User 1" in names
    assert "User 2" in names


async def _run_tests():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        await test_create_user(client)
        # await test_read_users(client)


if __name__ == "__main__":
    asyncio.run(_run_tests())
