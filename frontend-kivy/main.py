import asyncio
import threading
from datetime import datetime
import json

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock, mainthread

import httpx
import websockets
from plyer import notification

API_BASE = "http://127.0.0.1:8000"  # change to your server when needed
WS_URL   = "ws://127.0.0.1:8000/ws/alerts"

Builder.load_file("kv/app.kv")

class RootWidget(BoxLayout):
    def add_task(self):
        app = App.get_running_app()
        title = self.ids.title_in.text.strip()
        due_raw = self.ids.due_in.text.strip()
        if not title:
            return
        due_at = None
        if due_raw:
            # Expect ISO8601 like "2025-08-19T14:00:00Z" or "2025-08-19T14:00:00"
            try:
                # Let backend treat naive as UTC; keep it simple here
                due_at = datetime.fromisoformat(due_raw.replace("Z",""))
                due_at = due_at.isoformat()
            except Exception:
                due_at = None

        asyncio.run(app.api_create_task(title, due_at))
        self.ids.title_in.text = ""
        self.ids.due_in.text = ""
        asyncio.run(app.refresh_tasks())

class TodoApp(App):
    def build(self):
        self.title = "Kivy TODO"
        self.client = httpx.Client(timeout=10)
        root = RootWidget()
        Clock.schedule_once(lambda *_: asyncio.run(self.refresh_tasks()), 0.2)
        # Start WebSocket listener in a thread so Kivy main loop stays free
        threading.Thread(target=self._start_ws_thread, daemon=True).start()
        return root

    async def refresh_tasks(self):
        try:
            r = self.client.get(f"{API_BASE}/tasks")
            r.raise_for_status()
            tasks = r.json()
            # Convert None to "" for display
            for t in tasks:
                if t.get("due_at"):
                    # pretty short format
                    try:
                        dt = datetime.fromisoformat(t["due_at"].replace("Z",""))
                        t["due_at"] = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        pass
                else:
                    t["due_at"] = ""
            self._set_tasks(tasks)
        except Exception as e:
            print("Failed to fetch tasks:", e)

    @mainthread
    def _set_tasks(self, tasks):
        rv = self.root.ids.rv
        rv.data = [{"task_id": t["id"], "title": ("✓ " if t["completed"] else "• ") + t["title"], "due_at": t["due_at"]} for t in tasks]

    async def api_create_task(self, title: str, due_at_iso: str | None):
        payload = {"title": title, "completed": False, "due_at": due_at_iso}
        r = self.client.post(f"{API_BASE}/tasks", json=payload)
        r.raise_for_status()

    def toggle_task(self, task_id: int):
        # Fetch, flip completed, send patch
        try:
            r = self.client.get(f"{API_BASE}/tasks/{task_id}")
            r.raise_for_status()
            t = r.json()
            patch = {"completed": not t["completed"]}
            r2 = self.client.patch(f"{API_BASE}/tasks/{task_id}", json=patch)
            r2.raise_for_status()
            asyncio.run(self.refresh_tasks())
        except Exception as e:
            print("Toggle failed:", e)

    def delete_task(self, task_id: int):
        try:
            r = self.client.delete(f"{API_BASE}/tasks/{task_id}")
            if r.status_code in (200, 204):
                asyncio.run(self.refresh_tasks())
        except Exception as e:
            print("Delete failed:", e)

    # ---------- WebSocket listener ----------
    def _start_ws_thread(self):
        asyncio.run(self._ws_loop())

    async def _ws_loop(self):
        while True:
            try:
                async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
                    print("Connected to alerts WS.")
                    while True:
                        msg = await ws.recv()
                        self._handle_ws_message(msg)
            except Exception as e:
                print("WS disconnected, retrying in 2s:", e)
                await asyncio.sleep(2)

    def _handle_ws_message(self, msg: str):
        try:
            data = json.loads(msg)
            if data.get("type") == "task_due":
                t = data.get("task", {})
                title = t.get("title", "Task due")
                # Local notification (works on desktop & Android; iOS support depends on packaging)
                notification.notify(
                    title="Task Due",
                    message=title,
                    timeout=5  # seconds
                )
        except Exception as e:
            print("Bad WS message:", e)

if __name__ == "__main__":
    TodoApp().run()
