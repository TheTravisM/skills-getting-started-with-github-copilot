import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Original activities data for resetting
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball practice and league games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Outdoor soccer matches and skill building",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 22,
        "participants": []
    },
    "Drama Society": {
        "description": "Acting, stagecraft, and theatrical performances",
        "schedule": "Mondays and Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": []
    },
    "Art Studio": {
        "description": "Painting, sculpting, and mixed media art projects",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Debate Team": {
        "description": "Competitive debating and public speaking practice",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Robotics Club": {
        "description": "Design, build, and program robots for competition",
        "schedule": "Fridays, 3:30 PM - 6:00 PM",
        "max_participants": 10,
        "participants": []
    }
}


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test to ensure isolation."""
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)


def test_get_activities(client):
    """Test GET /activities returns all activities."""
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 200
    assert "Signed up test@mergington.edu for Chess Club" == response.json()["message"]
    
    # Verify data change
    activities_response = client.get("/activities")
    assert "test@mergington.edu" in activities_response.json()["Chess Club"]["participants"]


def test_signup_already_signed_up(client):
    """Test signup when student is already signed up."""
    # Arrange
    client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 200
    assert "test@mergington.edu is already signed up for Chess Club" == response.json()["message"]


def test_signup_activity_full(client):
    """Test signup when activity is full."""
    # Arrange: Fill the activity
    activity = activities["Chess Club"]
    activity["participants"] = ["email@mergington.edu"] * activity["max_participants"]
    
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 400
    assert "Activity is full" == response.json()["detail"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity."""
    # Act
    response = client.post("/activities/NonExistent/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]


def test_delete_success(client):
    """Test successful removal from an activity."""
    # Arrange
    client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 200
    assert "Removed test@mergington.edu from Chess Club" == response.json()["message"]
    
    # Verify data change
    activities_response = client.get("/activities")
    assert "test@mergington.edu" not in activities_response.json()["Chess Club"]["participants"]


def test_delete_participant_not_found(client):
    """Test delete when participant is not signed up."""
    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": "notsigned@mergington.edu"})
    
    # Assert
    assert response.status_code == 400
    assert "Participant not found" == response.json()["detail"]


def test_delete_activity_not_found(client):
    """Test delete for non-existent activity."""
    # Act
    response = client.delete("/activities/NonExistent/signup", params={"email": "test@mergington.edu"})
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]


def test_root_redirect(client):
    """Test GET / redirects to static/index.html."""
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"