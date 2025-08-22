import asyncio
import os
import sys
from time import sleep

# Prefer SDL2 window when running under Xvfb
if os.environ.get("DISPLAY"):
    os.environ.setdefault("KIVY_WINDOW", "sdl2")
else:
    os.environ.setdefault("KIVY_WINDOW", "mock")

os.environ.setdefault("SDL_VIDEODRIVER", "x11")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("KIVY_GL_BACKEND", "gl")
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_TEXT", "sdl2")
os.environ.setdefault("KIVY_AUDIO", "dummy")
os.environ.setdefault("KIVY_CLIPBOARD", "dummy")
os.environ.setdefault("KCFG_INPUT_MTDEV", "0")
os.environ.setdefault("XDG_RUNTIME_DIR", "/tmp")

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
    root = app.build()
    title = "Test task from Xvfb"
    root.ids.title_in.text = title
    root.ids.due_in.text = "2099-01-01T10:00:00"
    await app.api_create_task(title, "2099-01-01T10:00:00")

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/tasks")
        r.raise_for_status()
        tasks = r.json()
        ok = any(t["title"] == "Test task from Xvfb" for t in tasks)
        print("OK:" if ok else "FAIL:", "Task created and listed." if ok else "Task not created")
        if not ok:
            sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())