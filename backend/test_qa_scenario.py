import os
import sys
import time
import json
import sqlite3
import subprocess
import urllib.request

backend_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(backend_dir, "tasks.db")

print("==================================================")
print("QA TEST SCENARIO: MINI TASK MANAGER VERIFICATION")
print("==================================================")

# Step 1: Open the application with an empty database
print("\n[Step 1] Initializing fresh, empty SQLite database...")
if os.path.exists(db_path):
    os.remove(db_path)
    print("Previous tasks.db removed for clean test isolation.")

server_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=backend_dir
)

# Wait for server to be responsive
time.sleep(2)
for _ in range(10):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/tasks/", timeout=1) as resp:
            if resp.status == 200:
                initial_tasks = json.loads(resp.read().decode())
                assert initial_tasks == [], f"Expected empty task list, got {initial_tasks}"
                print("Confirmed: Application started with empty database. GET /tasks/ returned []")
                break
    except Exception:
        time.sleep(1)
else:
    print("FAILED: Server did not start.")
    server_proc.kill()
    sys.exit(1)

try:
    # Step 2: Create three different tasks
    print("\n[Step 2] Creating three distinct tasks...")
    tasks_to_create = [
        {"title": "Task Alpha: Review Code", "description": "Conduct thorough PR review"},
        {"title": "Task Beta: Run QA Suite", "description": "Execute automated integration tests"},
        {"title": "Task Gamma: Documentation", "description": "Write installation and verification guide"}
    ]

    created_tasks = []
    for task_data in tasks_to_create:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/tasks/",
            data=json.dumps(task_data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 201
            item = json.loads(resp.read().decode())
            created_tasks.append(item)
            print(f"  Created Task #{item['id']}: '{item['title']}' | Status: {item['status']}")

    assert len(created_tasks) == 3

    # Step 3: Confirm all three appear
    print("\n[Step 3] Confirming all three tasks appear via GET /tasks/...")
    with urllib.request.urlopen("http://127.0.0.1:8000/tasks/") as resp:
        assert resp.status == 200
        fetched_tasks = json.loads(resp.read().decode())
        assert len(fetched_tasks) == 3
        fetched_ids = {t["id"] for t in fetched_tasks}
        for ct in created_tasks:
            assert ct["id"] in fetched_ids
        print(f"Confirmed: All 3 tasks returned by server: {[t['title'] for t in fetched_tasks]}")

    task1_id = created_tasks[0]["id"]
    task2_id = created_tasks[1]["id"]
    task3_id = created_tasks[2]["id"]

    # Step 4: Complete the first task
    print(f"\n[Step 4] Completing the first task (ID #{task1_id})...")
    patch_req1 = urllib.request.Request(
        f"http://127.0.0.1:8000/tasks/{task1_id}/",
        data=json.dumps({"status": "Completed"}).encode(),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(patch_req1) as resp:
        assert resp.status == 200
        t1_updated = json.loads(resp.read().decode())
        assert t1_updated["status"] == "Completed"
        print(f"  Task #{task1_id} status updated to: {t1_updated['status']}")

    # Step 5: Complete the second task
    print(f"\n[Step 5] Completing the second task (ID #{task2_id})...")
    patch_req2 = urllib.request.Request(
        f"http://127.0.0.1:8000/tasks/{task2_id}/",
        data=json.dumps({"status": "Completed"}).encode(),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(patch_req2) as resp:
        assert resp.status == 200
        t2_updated = json.loads(resp.read().decode())
        assert t2_updated["status"] == "Completed"
        print(f"  Task #{task2_id} status updated to: {t2_updated['status']}")

    # Step 6: Keep the third task Pending
    print(f"\n[Step 6] Verifying third task (ID #{task3_id}) remains Pending...")
    with urllib.request.urlopen("http://127.0.0.1:8000/tasks/") as resp:
        tasks_now = {t["id"]: t for t in json.loads(resp.read().decode())}
        assert tasks_now[task3_id]["status"] == "Pending"
        print(f"  Task #{task3_id} status confirmed as: {tasks_now[task3_id]['status']}")

    # Step 7: Close and reopen the application (and restart backend server)
    print("\n[Step 7] Restarting backend server and simulating client close & reopen...")
    server_proc.terminate()
    server_proc.kill()
    server_proc.wait()
    print("  Backend process stopped.")

    time.sleep(1)
    # Restart server process
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir
    )
    time.sleep(2)
    print("  Backend process restarted with persistent SQLite database.")

    # Step 8: Verify all three tasks and their statuses
    print("\n[Step 8] Verifying all three tasks and statuses after application reload...")
    with urllib.request.urlopen("http://127.0.0.1:8000/tasks/") as resp:
        assert resp.status == 200
        reloaded_tasks = {t["id"]: t for t in json.loads(resp.read().decode())}
        assert len(reloaded_tasks) == 3

        print(f"  Task #{task1_id}: '{reloaded_tasks[task1_id]['title']}' => Status: {reloaded_tasks[task1_id]['status']}")
        print(f"  Task #{task2_id}: '{reloaded_tasks[task2_id]['title']}' => Status: {reloaded_tasks[task2_id]['status']}")
        print(f"  Task #{task3_id}: '{reloaded_tasks[task3_id]['title']}' => Status: {reloaded_tasks[task3_id]['status']}")

        assert reloaded_tasks[task1_id]["status"] == "Completed"
        assert reloaded_tasks[task2_id]["status"] == "Completed"
        assert reloaded_tasks[task3_id]["status"] == "Pending"

    # Step 9: Change the first task back to Pending
    print(f"\n[Step 9] Changing first task (ID #{task1_id}) back to Pending...")
    patch_req_revert = urllib.request.Request(
        f"http://127.0.0.1:8000/tasks/{task1_id}/",
        data=json.dumps({"status": "Pending"}).encode(),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(patch_req_revert) as resp:
        assert resp.status == 200
        t1_reverted = json.loads(resp.read().decode())
        assert t1_reverted["status"] == "Pending"
        print(f"  Task #{task1_id} status successfully reverted to: {t1_reverted['status']}")

    # Step 10: Verify the updated database records directly in SQLite
    print("\n[Step 10] Verifying database records directly in SQLite tasks.db...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status FROM tasks ORDER BY id ASC")
    db_rows = cursor.fetchall()
    conn.close()

    print("  SQLite rows found in database:")
    for row in db_rows:
        print(f"    - ID: {row[0]}, Title: '{row[1]}', Status: '{row[2]}'")

    assert len(db_rows) == 3
    assert db_rows[0][0] == task1_id and db_rows[0][2] == "Pending", "Task 1 should be Pending in DB"
    assert db_rows[1][0] == task2_id and db_rows[1][2] == "Completed", "Task 2 should be Completed in DB"
    assert db_rows[2][0] == task3_id and db_rows[2][2] == "Pending", "Task 3 should be Pending in DB"

    print("\n==================================================")
    print("ALL 10 QA INTEGRATION SCENARIO STEPS PASSED 100%!")
    print("==================================================")

finally:
    server_proc.terminate()
    server_proc.kill()

