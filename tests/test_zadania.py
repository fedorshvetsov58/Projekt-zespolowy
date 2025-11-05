import pytest
import json
import jwt
from datetime import datetime, timedelta
from app import SECRET_KEY
from app import app, get_db_connection


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        init_db()
        conn = get_db_connection()
        conn.execute("DELETE FROM zadania")
        conn.execute("DELETE FROM users")
        conn.commit()
        conn.close()
    with app.test_client() as client:
        yield client

def make_token():
    return jwt.encode({"user_id": 1, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")

def test_get_zadania_empty(client):
    response = client.get("/api/zadania")
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_zadanie(client):
    token = make_token()
    data = {
        "tytul": "Test task",
        "opis": "Opis testowego zadania",
        "deadline": "2025-12-31",
        "priorytet": "wysoki"
    }
    response = client.post("/api/zadania", json=data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

def test_create_zadanie_missing_field(client):
    token = make_token()
    response = client.post("/api/zadania", json={"tytul": "abc"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400