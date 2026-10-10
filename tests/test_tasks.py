from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models
from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_deployflow.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db() -> Generator[Session]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "DeployFlow Task API"


def test_liveness_check():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_check():
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Learn FastAPI",
            "description": "Build the Day 1 API",
            "status": "TODO",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Learn FastAPI"
    assert data["status"] == "TODO"
    assert "id" in data


def test_list_tasks():
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2", "status": "DONE"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_tasks_by_status():
    client.post("/tasks", json={"title": "Task 1", "status": "TODO"})
    client.post("/tasks", json={"title": "Task 2", "status": "DONE"})

    response = client.get("/tasks?status=DONE")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "DONE"


def test_get_task_by_id():
    create_response = client.post("/tasks", json={"title": "Read task"})
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task():
    create_response = client.post("/tasks", json={"title": "Old title"})
    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "New title",
            "status": "IN_PROGRESS",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["status"] == "IN_PROGRESS"


def test_delete_task():
    create_response = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    get_response = client.get(f"/tasks/{task_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_invalid_task_title():
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_missing_task_id():
    response = client.get("/tasks/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404