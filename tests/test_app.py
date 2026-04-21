import os
import sys
import tempfile
import pytest

# Add project root folder to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as myapp


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()

    myapp.app.config["TESTING"] = True
    myapp.DB_NAME = db_path

    myapp.init_db()

    with myapp.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def login(client, username="admin", password="admin"):
    return client.post("/", data={
        "username": username,
        "password": password
    }, follow_redirects=True)


def test_login_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest Login" in response.data


def test_invalid_login(client):
    response = client.post("/", data={
        "username": "wrong",
        "password": "wrong"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_valid_login(client):
    response = login(client)
    assert response.status_code == 200
    assert b"Welcome to ACEest Dashboard" in response.data


def test_protected_clients_page_redirects_when_not_logged_in(client):
    response = client.get("/clients", follow_redirects=True)
    assert response.status_code == 200
    assert b"ACEest Login" in response.data


def test_add_client_and_view_in_list(client):
    # login first
    login_response = login(client)
    assert b"Welcome to ACEest Dashboard" in login_response.data

    # add a client
    add_response = client.post("/add-client", data={
        "name": "Rahul",
        "age": "25",
        "height": "172",
        "weight": "70",
        "program": "Muscle Gain"
    }, follow_redirects=True)

    assert add_response.status_code == 200
    assert b"Client added successfully" in add_response.data

    # open client list
    list_response = client.get("/clients", follow_redirects=True)
    assert list_response.status_code == 200
    assert b"Rahul" in list_response.data
    assert b"Muscle Gain" in list_response.data