import asyncio
import sys
from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.main import app, manager
from backend import db


@pytest.fixture
def client(monkeypatch):
    """Create a TestClient with an in-memory database."""
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "get_session", lambda: Session(engine))

    with TestClient(app) as c:
        yield c


def test_crud_lifecycle(client):
    payload = {"title": "Test", "completed": False, "due_at": None}
    resp = client.post("/tasks", json=payload)
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    resp = client.get("/tasks")
    assert any(t["id"] == task_id for t in resp.json())

    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test"

    resp = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert resp.status_code == 200
    assert resp.json()["completed"] is True

    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 404


def test_parses_due_at_from_title_on_create(client):
    payload = {"title": "Pay bills on July 15 2030 at 5pm"}
    resp = client.post("/tasks", json=payload)
    assert resp.status_code == 201
    assert resp.json()["due_at"].startswith("2030-07-15T17:00:00")


def test_parses_due_at_from_title_on_update(client):
    resp = client.post("/tasks", json={"title": "No date"})
    task_id = resp.json()["id"]
    resp = client.patch(f"/tasks/{task_id}", json={"title": "Meet on Aug 1 2030 09:00"})
    assert resp.status_code == 200
    assert resp.json()["due_at"].startswith("2030-08-01T09:00:00")


def test_parsed_due_at_normalized_to_utc(client):
    resp = client.post("/tasks", json={"title": "Meet on Aug 1 2030 09:00 PDT"})
    assert resp.status_code == 201
    assert resp.json()["due_at"].startswith("2030-08-01T16:00:00")


def test_websocket_broadcast(client):
    with client.websocket_connect("/ws/alerts") as ws:
        asyncio.get_event_loop().run_until_complete(manager.broadcast({"ping": "pong"}))
        data = ws.receive_json()
        assert data == {"ping": "pong"}
