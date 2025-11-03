import random
import pytest
from app import app
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register_validation_errors(client):
    # za krotki password
    res = client.post("/register", json={"login": "abc", "password": "12"})
    assert res.status_code == 422
    assert any(err["field"] == "password" for err in res.json["fieldErrors"])

    # niepoprawny login (spacja)
    res2 = client.post("/register", json={"login": "ab c", "password": "123456"})
    assert res2.status_code == 422
    assert any(err["field"] == "login" for err in res2.json["fieldErrors"])

    # poprawny login (bez spacji i bez podkreślnika)
    name = f"validuser{random.randint(1,1000)}"
    res3 = client.post("/register", json={"login": name, "password": "123456"})
    assert res3.status_code == 201

    # duplikat loginu
    res4 = client.post("/register", json={"login": name, "password": "123456"})
    assert res4.status_code == 409