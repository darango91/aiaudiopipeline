"""
Integration tests for the AI Audio backend.
"""
import os
import pytest
import json
from fastapi.testclient import TestClient
import asyncio
from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def test_audio_file():
    """Fixture for test audio file path."""
    # Path to a test audio file in the tests directory
    return os.path.join(os.path.dirname(__file__), "data", "test_audio.wav")

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_session():
    """Test creating a new audio session."""
    response = client.post(
        "/api/audio/sessions",
        json={"title": "Test Session", "description": "Test session description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["title"] == "Test Session"
    assert data["description"] == "Test session description"
    
    return data["session_id"]

def test_get_session():
    """Test retrieving an audio session."""
    # First create a session
    session_id = test_create_session()
    
    # Then retrieve it
    response = client.get(f"/api/audio/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["title"] == "Test Session"

def test_update_session():
    """Test updating an audio session."""
    # First create a session
    session_id = test_create_session()
    
    # Then update it
    response = client.put(
        f"/api/audio/sessions/{session_id}",
        json={"title": "Updated Session", "description": "Updated description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Session"
    assert data["description"] == "Updated description"

def test_upload_audio_file(test_audio_file):
    """Test uploading an audio file."""
    # First create a session
    session_id = test_create_session()
    
    # Then upload an audio file
    with open(test_audio_file, "rb") as f:
        response = client.post(
            "/api/audio/upload",
            files={"audio_file": ("test_audio.wav", f, "audio/wav")},
            data={"session_id": session_id}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert len(data["transcript"]) > 0

def test_keyword_crud():
    """Test CRUD operations for keywords."""
    # Create a keyword
    response = client.post(
        "/api/keywords",
        json={
            "text": "test keyword",
            "description": "A test keyword",
            "threshold": 0.7
        }
    )
    assert response.status_code == 201
    data = response.json()
    keyword_id = data["id"]
    
    # Get the keyword
    response = client.get(f"/api/keywords/{keyword_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "test keyword"
    
    # Update the keyword
    response = client.put(
        f"/api/keywords/{keyword_id}",
        json={
            "text": "updated keyword",
            "description": "An updated test keyword",
            "threshold": 0.8
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "updated keyword"
    
    # Delete the keyword
    response = client.delete(f"/api/keywords/{keyword_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(f"/api/keywords/{keyword_id}")
    assert response.status_code == 404

def test_talking_point_crud():
    """Test CRUD operations for talking points."""
    # First create a keyword
    response = client.post(
        "/api/keywords",
        json={
            "text": "test keyword",
            "description": "A test keyword",
            "threshold": 0.7
        }
    )
    keyword_id = response.json()["id"]
    
    # Create a talking point
    response = client.post(
        f"/api/keywords/{keyword_id}/talking-points",
        json={
            "title": "Test Talking Point",
            "content": "This is a test talking point",
            "priority": 1
        }
    )
    assert response.status_code == 201
    data = response.json()
    talking_point_id = data["id"]
    
    # Get the talking point
    response = client.get(f"/api/keywords/{keyword_id}/talking-points/{talking_point_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Talking Point"
    
    # Update the talking point
    response = client.put(
        f"/api/keywords/{keyword_id}/talking-points/{talking_point_id}",
        json={
            "title": "Updated Talking Point",
            "content": "This is an updated test talking point",
            "priority": 2
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Talking Point"
    
    # Delete the talking point
    response = client.delete(f"/api/keywords/{keyword_id}/talking-points/{talking_point_id}")
    assert response.status_code == 200
    
    # Clean up the keyword
    client.delete(f"/api/keywords/{keyword_id}")

# Create a test directory for audio files
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

# Create a simple test audio file if it doesn't exist
test_audio_path = os.path.join(os.path.dirname(__file__), "data", "test_audio.wav")
if not os.path.exists(test_audio_path):
    # This is a placeholder - in a real test, you would have an actual audio file
    with open(test_audio_path, "wb") as f:
        # Write a minimal WAV header and some sample data
        # This is not a valid WAV file but serves as a placeholder for tests
        f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xAC\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
