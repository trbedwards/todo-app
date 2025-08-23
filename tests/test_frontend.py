import asyncio
import sys
from pathlib import Path

import httpx
import pytest
from sqlmodel import SQLModel, create_engine, Session

import uvicorn
import threading
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.main import app as backend_app
import backend.db as db


@pytest.fixture
def todo_app(monkeypatch):
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "get_session", lambda: Session(engine))

    config = uvicorn.Config(backend_app, host="127.0.0.1", port=8001, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)

    frontend_dir = Path(__file__).resolve().parent.parent / "frontend-kivy"
    monkeypatch.chdir(frontend_dir)
    sys.path.append(str(frontend_dir))
    import main as frontend_main
    frontend_main.API_BASE = "http://127.0.0.1:8001"
    frontend_main.WS_URL = "ws://127.0.0.1:8001/ws/alerts"

    app = frontend_main.TodoApp()
    app.client = httpx.Client(base_url=frontend_main.API_BASE, timeout=10)
    root = frontend_main.RootWidget()
    app.root = root

    yield app, frontend_main

    app.client.close()
    server.should_exit = True
    thread.join()
    sys.path.remove(str(frontend_dir))


def test_add_toggle_delete(todo_app):
    app, frontend_main = todo_app
    asyncio.run(app.api_create_task("from front", None))
    tasks = app.client.get(f"{frontend_main.API_BASE}/tasks").json()
    frontend_main.TodoApp._set_tasks.__wrapped__(app, tasks)
    rv = app.root.ids.rv
    assert any("from front" in item["title"] for item in rv.data)

    task_id = rv.data[0]["task_id"]
    app.toggle_task(task_id)
    tasks = app.client.get(f"{frontend_main.API_BASE}/tasks").json()
    frontend_main.TodoApp._set_tasks.__wrapped__(app, tasks)
    rv = app.root.ids.rv
    assert any(i["task_id"] == task_id and i["title"].startswith("\u2713") for i in rv.data)

    app.delete_task(task_id)
    tasks = app.client.get(f"{frontend_main.API_BASE}/tasks").json()
    frontend_main.TodoApp._set_tasks.__wrapped__(app, tasks)
    rv = app.root.ids.rv
    assert all(i["task_id"] != task_id for i in rv.data)
