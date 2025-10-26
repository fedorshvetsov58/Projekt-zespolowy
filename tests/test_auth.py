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

def test_register_and_login(client):
    # unused_log
    login_name = f"testuser_{random.randint(1, 10000)}"

    # log
    res = client.post("/register", json={"login": login_name, "password": "123456"})
    assert res.status_code == 201

    # reg
    res2 = client.post("/login", json={"login": login_name, "password": "123456"})
    assert res2.status_code == 200
    assert "token" in res2.json