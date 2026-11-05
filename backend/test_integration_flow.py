import subprocess
import sys
import time
import urllib.request
import json
import sqlite3
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(backend_dir, "tasks.db")

print("--- Step 1: Launch FastAPI Server ---")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=backend_dir
)

# Wait for server to bind
started = False
for _ in range(15):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1) as r:
            if r.status == 200:
                started = True
                print("FastAPI server started successfully on http://127.0.0.1:8000")
                break
    except Exception:
        time.sleep(1)

if not started:
    print("Error: FastAPI failed to start")
    proc.kill()
    sys.exit(1)

try:
    print("\n--- Step 2: Simulate Mobile App - Add Task ---")
    post_data = json.dumps({
        "title": "Build Flutter UI Integration",
        "description": "Complete assignment Phase 4"
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/tasks/",
        data=post_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        assert resp.status == 201, f"Expected 201, got {resp.status}"
        created_task = json.loads(resp.read().decode("utf-8"))
        print(f"Task created via API: ID={created_task['id']}, Title='{created_task['title']}', Status='{created_task['status']}'")
        task_id = created_task["id"]

    print("\n--- Step 3: Verify Task Appears in SQLite Database ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, status, created_at FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None, f"Task {task_id} not found in SQLite tasks.db"
    print(f"SQLite DB Record Verified: ID={row[0]}, Title='{row[1]}', Description='{row[2]}', Status='{row[3]}'")
    assert row[3] == "Pending", f"Expected Pending, found {row[3]}"

    print("\n--- Step 4: Mark Task as Completed via Mobile Client ---")
    patch_data = json.dumps({"status": "Completed"}).encode("utf-8")
    patch_req = urllib.request.Request(
        f"http://127.0.0.1:8000/tasks/{task_id}/",
        data=patch_data,
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )

    with urllib.request.urlopen(patch_req) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        updated_task = json.loads(resp.read().decode("utf-8"))
        print(f"Task updated via API: ID={updated_task['id']}, Status='{updated_task['status']}'")
        assert updated_task["status"] == "Completed"

    print("\n--- Step 5: Verify Updated Status in SQLite Database ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
    updated_status = cursor.fetchone()[0]
    conn.close()

    print(f"SQLite DB Updated Status Verified: '{updated_status}'")
    assert updated_status == "Completed"

    print("\n--- Step 6: Restart App Simulation - Fetch Tasks ---")
    with urllib.request.urlopen("http://127.0.0.1:8000/tasks/") as resp:
        assert resp.status == 200
        all_tasks = json.loads(resp.read().decode("utf-8"))
        matching = [t for t in all_tasks if t["id"] == task_id]
        assert len(matching) == 1
        persisted = matching[0]
        print(f"Task Verified After Client Re-fetch: ID={persisted['id']}, Status='{persisted['status']}'")
        assert persisted["status"] == "Completed"

    print("\nAll integration verification steps PASSED successfully!")

finally:
    proc.terminate()
    proc.kill()
