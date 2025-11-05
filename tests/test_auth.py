import random
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from database import init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        init_db()
    with app.test_client() as client:
        yield client


def test_register_validation_errors(client):
    # za krotki password
    res = client.post("/register", json={"login": "abc", "password": "12"})
    assert res.status_code == 422
    assert any(err["field"] == "password" for err in res.json["fieldErrors"])

    # niepoprawny login
    res2 = client.post("/register", json={"login": "ab c", "password": "123456"})
    assert res2.status_code == 422
    assert any(err["field"] == "login" for err in res2.json["fieldErrors"])

    # poprawny login
    name = f"validuser{random.randint(1,1000)}"
    res3 = client.post("/register", json={"login": name, "password": "123456"})
    assert res3.status_code == 201

    # duplikat loginu
    res4 = client.post("/register", json={"login": name, "password": "123456"})
    assert res4.status_code == 409
