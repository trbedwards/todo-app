import asyncio
import os
import sys
from time import sleep

# Ensure Kivy runs without a window (headless)
os.environ.setdefault("KIVY_WINDOW", "mock")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("KIVY_GL_BACKEND", "mock")
os.environ.setdefault("KIVY_BCM_DISPMANX_ID", "0")
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_TEXT", "dummy")
os.environ.setdefault("KIVY_AUDIO", "dummy")
os.environ.setdefault("XDG_RUNTIME_DIR", "/tmp")

from kivy.base import EventLoop
from kivy.config import Config
Config.set("kivy", "log_level", "info")
Config.set("input", "mouse", "mouse")

from main import TodoApp
import httpx

API_BASE = "http://127.0.0.1:8000"

async def wait_server():
    for _ in range(50):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{API_BASE}/tasks")
                if r.status_code == 200:
                    return True
        except Exception:
            pass
        await asyncio.sleep(0.1)
    return False

async def main():
    ok = await wait_server()
    if not ok:
        print("Server not responding", file=sys.stderr)
        sys.exit(2)

    app = TodoApp()
    # Build without starting full run loop
    root = app.build()
    # Simulate entering title and due date
    root.ids.title_in.text = "Test task from CI"
    root.ids.due_in.text = "2099-01-01T10:00:00"
    # Call add_task (which calls backend synchronously via httpx)
    root.add_task()

    # Fetch tasks and assert our task exists
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/tasks")
        r.raise_for_status()
        tasks = r.json()
        assert any(t["title"] == "Test task from CI" for t in tasks), "Task not created"
        print("OK: Task created and listed.")

if __name__ == "__main__":
    asyncio.run(main())