from fastapi.testclient import TestClient
from pprint import pprint

def test_create_expense(client: TestClient):
    # Setup: Create Group and User directly in DB or via API
    # Since we don't have direct DB access easily here without session fixture, 
    # we can use API to create user/group first or just mock IDs if we didn't enforce FK in sqlite (but we do).
    # So we need to create user and group first.
    
    # Create User
    user_payload = {"name": "Alice"}
    user_resp = client.post("/users", json=user_payload)
    assert user_resp.status_code == 200
    user_id = user_resp.json()["id"]

    # Create Group (we don't have group endpoint in the snippets I saw, but assuming there is one or we need to insert it)
    # Wait, I didn't see a groups router. 
    # Let's check if I can insert directly using session fixture if I inject it.
    # But for now, let's assume we need to create them.
    # If there is no group router, I might need to use the session fixture in the test.
    pass 

# Re-writing the test to use session fixture for setup
def test_create_expense_full(client: TestClient, session):
    from app.models import User, Group
    
    user = User(name="Alice")
    session.add(user)
    
    group = Group(name="Lunch Group")
    session.add(group)
    
    session.commit()
    session.refresh(user)
    session.refresh(group)
    
    payload = {
        "title": "Lunch",
        "amount": "50.00",
        "group_id": group.id,
        "user_id": user.id,
    }

    response = client.post("/expenses", json=payload)
    data = response.json()
    pprint(data)
    assert response.status_code == 200
    assert data["title"] == "Lunch"
    assert data["amount"] == 50.00


def test_read_expenses(client: TestClient, session):
    from app.models import User, Group, Expense
    
    user = User(name="Bob")
    session.add(user)
    group = Group(name="Dinner Group")
    session.add(group)
    session.commit()
    session.refresh(user)
    session.refresh(group)

    # Create expense via API
    payload = {
        "title": "Dinner",
        "amount": "100.00",
        "group_id": group.id,
        "user_id": user.id,
    }
    client.post("/expenses", json=payload)

    response = client.get("/expenses")
    data = response.json()
    pprint(data)
    assert response.status_code == 200
    assert len(data) >= 1
