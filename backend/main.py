from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from typing import List, Set
from datetime import datetime, timezone
import asyncio

from .db import init_db, get_session, engine
from .models import Task, TaskCreate, TaskRead, TaskUpdate
from sqlmodel import Session

app = FastAPI(title="TODO API")

# CORS so Kivy (or RN later) can talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# ---------- CRUD ----------
@app.get("/tasks", response_model=List[TaskRead])
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task).order_by(Task.id.desc())).all()

@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)):
    task = Task(**payload.dict())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=TaskRead)
def patch_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(task, k, v)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    session.delete(task)
    session.commit()
    return

# ---------- Alerts via WebSocket ----------
# Simple in-memory broadcaster
class ConnectionManager:
    def __init__(self):
        self.active: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()
# Keep track of which reminders were sent (very naive)
_sent_reminders: Set[int] = set()

@app.websocket("/ws/alerts")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            # keep the socket alive; we don’t receive messages in this demo
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        manager.disconnect(ws)

# Background scheduler (simple loop) – checks due tasks and emits once
async def reminder_scheduler():
    await asyncio.sleep(1)
    while True:
        try:
            from .models import Task
            # create and close sessions manually in this background task
            with Session(engine) as session:
                now = datetime.now(timezone.utc)
                tasks = session.exec(select(Task).where(Task.completed == False)).all()
                for t in tasks:
                    if t.due_at:
                        due = t.due_at
                        if due.tzinfo is None:
                            # treat naive as UTC for demo
                            due = due.replace(tzinfo=timezone.utc)
                        # Send when past due and not sent yet
                        if due <= now and t.id not in _sent_reminders:
                            await manager.broadcast({
                                "type": "task_due",
                                "task": {
                                    "id": t.id,
                                    "title": t.title,
                                    "due_at": t.due_at.isoformat()
                                }
                            })
                            _sent_reminders.add(t.id)
        except Exception:
            # swallow in demo; log in real app
            pass
        await asyncio.sleep(2)  # check every 2s (demo)

@app.on_event("startup")
async def start_scheduler():
    asyncio.create_task(reminder_scheduler())
