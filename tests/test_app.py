import pytest

from app import create_app

@pytest.fixture()
def app(tmp_path):
database_path = tmp_path / "test_tickets.db"

```
app = create_app(
    {
        "TESTING": True,
        "DATABASE": str(database_path),
        "SECRET_KEY": "test-only-secret",
    }
)

yield app
```

@pytest.fixture()
def client(app):
return app.test_client()

def test_health_endpoint(client):
response = client.get("/health")

```
assert response.status_code == 200
assert response.json == {
    "status": "ok",
    "database": "ok",
}
```

def test_list_tickets_initially_empty(client):
response = client.get("/tickets")

```
assert response.status_code == 200
assert response.json == []
```

def test_create_ticket(client):
response = client.post(
"/tickets",
json={
"title": "Login page issue",
"description": "The login page returns an unexpected error.",
},
)

```
assert response.status_code == 201
assert response.json["title"] == "Login page issue"
assert response.json["description"] == (
    "The login page returns an unexpected error."
)
assert response.json["status"] == "open"
assert "id" in response.json
```

def test_get_existing_ticket(client):
create_response = client.post(
"/tickets",
json={"title": "Test ticket"},
)

```
ticket_id = create_response.json["id"]

response = client.get(f"/tickets/{ticket_id}")

assert response.status_code == 200
assert response.json["id"] == ticket_id
assert response.json["title"] == "Test ticket"
```

def test_get_missing_ticket(client):
response = client.get("/tickets/999")

```
assert response.status_code == 404
assert response.json["error"] == "Ticket not found"
```

def test_reject_missing_title(client):
response = client.post(
"/tickets",
json={"description": "Missing title"},
)

```
assert response.status_code == 400
```

def test_reject_empty_title(client):
response = client.post(
"/tickets",
json={"title": "   "},
)

```
assert response.status_code == 400
```

def test_reject_invalid_content_type(client):
response = client.post(
"/tickets",
data="title=Example",
content_type="application/x-www-form-urlencoded",
)

```
assert response.status_code == 415
```

def test_reject_invalid_status(client):
response = client.post(
"/tickets",
json={
"title": "Test ticket",
"status": "unauthorized",
},
)

```
assert response.status_code == 400
```

def test_reject_unknown_fields(client):
response = client.post(
"/tickets",
json={
"title": "Test ticket",
"is_admin": True,
},
)

```
assert response.status_code == 400
```

def test_update_ticket(client):
create_response = client.post(
"/tickets",
json={"title": "Original title"},
)

```
ticket_id = create_response.json["id"]

response = client.patch(
    f"/tickets/{ticket_id}",
    json={
        "title": "Updated title",
        "status": "in_progress",
    },
)

assert response.status_code == 200
assert response.json["title"] == "Updated title"
assert response.json["status"] == "in_progress"
```

def test_update_missing_ticket(client):
response = client.patch(
"/tickets/999",
json={"title": "Updated title"},
)

```
assert response.status_code == 404
```

def test_delete_ticket(client):
create_response = client.post(
"/tickets",
json={"title": "Ticket to delete"},
)

```
ticket_id = create_response.json["id"]

delete_response = client.delete(
    f"/tickets/{ticket_id}"
)

assert delete_response.status_code == 204

get_response = client.get(
    f"/tickets/{ticket_id}"
)

assert get_response.status_code == 404
```

def test_delete_missing_ticket(client):
response = client.delete("/tickets/999")

```
assert response.status_code == 404
```

def test_sql_injection_payload_is_treated_as_data(client):
payload = "' OR 1=1 --"

```
create_response = client.post(
    "/tickets",
    json={"title": payload},
)

assert create_response.status_code == 201
assert create_response.json["title"] == payload

response = client.get("/tickets")

assert response.status_code == 200
assert len(response.json) == 1
assert response.json[0]["title"] == payload
```
