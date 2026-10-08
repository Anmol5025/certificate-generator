from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

from app.main import app, get_db
from app.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_job():
    response = client.post(
        "/jobs",
        json={
            "recipients": [
                {"name": "Alice", "email": "alice@example.com", "course": "Python 101"},
                {"name": "Bob", "email": "bob@example.com", "course": "Python 101"}
            ]
        }
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "pending"
    assert "id" in data
    
    job_id = data["id"]
    
    # Wait a bit for background task to complete
    time.sleep(2)
    
    # Check status
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["certificates"]) == 2
    
    cert_id = data["certificates"][0]["id"]
    assert data["certificates"][0]["status"] == "success"
    
    # Download
    response = client.get(f"/certificates/{cert_id}/download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_invalid_input():
    response = client.post(
        "/jobs",
        json={
            "recipients": [
                {"name": "Alice", "email": "not-an-email", "course": "Python 101"}
            ]
        }
    )
    assert response.status_code == 422
    
    response = client.post(
        "/jobs",
        json={
            "recipients": []
        }
    )
    assert response.status_code == 400
