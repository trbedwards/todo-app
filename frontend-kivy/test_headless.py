import asyncio
import httpx
import pytest

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

@pytest.mark.asyncio
async def test_create_task_listed():
    assert await wait_server(), "Server not responding"

    title = "Test task from Xvfb"
    due = "2099-01-01T10:00:00"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/tasks",
            json={"title": title, "completed": False, "due_at": due},
        )
        assert resp.status_code in (200, 201)

        list_resp = await client.get(f"{API_BASE}/tasks")
        assert list_resp.status_code == 200
        tasks = list_resp.json()
        assert any(t["title"] == title for t in tasks)
