# Mini Task Manager - FastAPI Backend

This is the Python FastAPI backend for the Mini Task Manager mobile application. It persists data in SQLite (`tasks.db`) and provides REST APIs for task management.

## Prerequisites

- Python 3.10+ (tested on Python 3.13)
- Windows PowerShell / Terminal

## Installation

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   py -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # Or Command Prompt:
   .\.venv\Scripts\activate.bat
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the FastAPI application with Uvicorn:

```bash
# Direct command (with .venv):
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Base URL:** `http://127.0.0.1:8000` or `http://localhost:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

## Running Automated Tests

Run the comprehensive pytest suite:

```bash
.\.venv\Scripts\pytest.exe -v
```

All tests run against an isolated in-memory SQLite database, leaving `tasks.db` untouched.

## API Specification

### 1. `GET /tasks/`
- **Description:** Retrieve all tasks.
- **Status Code:** `200 OK`
- **Response:** JSON Array of tasks:
  ```json
  [
    {
      "id": 1,
      "title": "Complete assignment",
      "description": "Finish Flutter task manager",
      "status": "Pending",
      "created_at": "2026-11-05T12:00:00Z"
    }
  ]
  ```

### 2. `POST /tasks/`
- **Description:** Create a new task.
- **Status Code:** `201 Created`
- **Request Body:**
  ```json
  {
    "title": "Complete assignment",
    "description": "Finish Flutter task manager"
  }
  ```
- **Validation:** `title` is required and must not be empty or whitespace only.
- **Initial Status:** Automatically sets `"Pending"`.

### 3. `PATCH /tasks/{id}/`
- **Description:** Update the status of an existing task.
- **Status Code:** `200 OK` (or `404 Not Found` if task ID does not exist; `422 Unprocessable Entity` for invalid status).
- **Request Body:**
  ```json
  {
    "status": "Completed"
  }
  ```
  *(Allowed values: `"Pending"` or `"Completed"`)*

