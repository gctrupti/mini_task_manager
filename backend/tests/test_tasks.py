import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Create an in-memory SQLite database strictly for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Create fresh tables for every test and drop them afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_tasks_empty(client):
    """GET /tasks/ should return 200 with an empty JSON array if no tasks exist."""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_post_task_valid(client):
    """POST /tasks/ should validate, save to SQLite, assign 'Pending' status, and return 201."""
    payload = {
        "title": "Complete assignment",
        "description": "Finish Flutter task manager"
    }
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Complete assignment"
    assert data["description"] == "Finish Flutter task manager"
    assert data["status"] == "Pending"
    assert "created_at" in data


def test_post_task_without_description(client):
    """POST /tasks/ should succeed when description is omitted (optional)."""
    payload = {"title": "Task without description"}
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task without description"
    assert data["description"] is None
    assert data["status"] == "Pending"


def test_post_task_empty_title(client):
    """POST /tasks/ should reject empty or whitespace-only titles with 422."""
    payload = {"title": "   ", "description": "Some description"}
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 422


def test_post_task_missing_title(client):
    """POST /tasks/ should reject payloads missing the title field with 422."""
    payload = {"description": "Missing title"}
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 422


def test_get_tasks_populated(client):
    """GET /tasks/ should return all created tasks."""
    client.post("/tasks/", json={"title": "Task 1", "description": "Desc 1"})
    client.post("/tasks/", json={"title": "Task 2", "description": "Desc 2"})

    response = client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    titles = [t["title"] for t in tasks]
    assert "Task 1" in titles
    assert "Task 2" in titles


def test_patch_pending_to_completed(client):
    """PATCH /tasks/{id}/ should successfully update status to Completed."""
    create_res = client.post("/tasks/", json={"title": "Test Task", "description": "Desc"})
    task_id = create_res.json()["id"]

    patch_res = client.patch(f"/tasks/{task_id}/", json={"status": "Completed"})
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["id"] == task_id
    assert updated_data["status"] == "Completed"


def test_patch_completed_to_pending(client):
    """PATCH /tasks/{id}/ should successfully toggle status from Completed back to Pending."""
    create_res = client.post("/tasks/", json={"title": "Test Task"})
    task_id = create_res.json()["id"]

    # First mark as Completed
    client.patch(f"/tasks/{task_id}/", json={"status": "Completed"})

    # Then toggle back to Pending
    patch_res = client.patch(f"/tasks/{task_id}/", json={"status": "Pending"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "Pending"


def test_patch_invalid_task_id(client):
    """PATCH /tasks/{id}/ with nonexistent ID should return 404."""
    response = client.patch("/tasks/999999/", json={"status": "Completed"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_patch_invalid_status(client):
    """PATCH /tasks/{id}/ with invalid status string should return 422."""
    create_res = client.post("/tasks/", json={"title": "Test Task"})
    task_id = create_res.json()["id"]

    response = client.patch(f"/tasks/{task_id}/", json={"status": "In Progress"})
    assert response.status_code == 422


def test_delete_task_success(client):
    """DELETE /tasks/{id}/ should delete task and return 204."""
    create_res = client.post("/tasks/", json={"title": "To Delete", "description": "Will be removed"})
    task_id = create_res.json()["id"]

    del_res = client.delete(f"/tasks/{task_id}/")
    assert del_res.status_code == 204

    # Verify task is no longer returned in GET /tasks/
    get_res = client.get("/tasks/")
    tasks = get_res.json()
    assert all(t["id"] != task_id for t in tasks)


def test_delete_task_not_found(client):
    """DELETE /tasks/{id}/ with nonexistent ID should return 404."""
    del_res = client.delete("/tasks/999999/")
    assert del_res.status_code == 404


def test_docs_and_health(client):
    """Ensure root health and /docs endpoints are functional."""
    health_res = client.get("/")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    docs_res = client.get("/docs")
    assert docs_res.status_code == 200

