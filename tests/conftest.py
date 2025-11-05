import pytest
from app import app
from database import init_db, get_db_connection
from app import app
import os
import tempfile

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config["TESTING"] = True
    app.config["DATABASE"] = db_path

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(db_path)