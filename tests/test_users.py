from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post("/users", json={"name": "Test User"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert "id" in data


def test_read_users(client: TestClient):
    # Create a user first
    client.post("/users", json={"name": "User Man"})
    client.post("/users", json={"name": "User Woman"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [u["name"] for u in data]
    assert "User Man" in names
    assert "User Woman" in names
