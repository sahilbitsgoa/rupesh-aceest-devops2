import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest Fitness Flask App" in response.data

def test_init_db_route():
    client = app.test_client()
    response = client.get("/init-db")
    assert response.status_code == 200
    assert b"Database initialized successfully" in response.data

def test_login_page_loads():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data

def test_invalid_login():
    client = app.test_client()
    response = client.post(
        "/login",
        data={
            "username": "wronguser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data