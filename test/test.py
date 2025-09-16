import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.dependencies import get_db
from app.main import app

# Use an in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables before tests start
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Provide a test client
@pytest.fixture()
def client():
    return TestClient(app)


# --- Tests ---
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Crowdsource Crime alert system"}

def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword",
            "fullname": "Test User",
            "role": "user"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["message"] == "User created successfully"

def test_login(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_me(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        },
    )
    token = response.json()["access_token"]

    response = client.get(
        "/auth/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["fullname"] == "Test User"
    assert data["role"] == "user"


def test_update_user_profile(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        },
    )
    token = response.json()["access_token"]

    response = client.put(
        "/auth/users/me",
        json={
            "fullname": "Updated User",
            "username": "updateduser",
            "old_password": "testpassword",
            "new_password": "newpassword"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["fullname"] == "Updated User"

    # Verify login with new credentials
    response = client.post(
        "/auth/login",
        data={
            "username": "updateduser",
            "password": "newpassword"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"



def test_create_crime(client):
    # First, login to get a token
    response = client.post(
        "/auth/login",
        data={
            "username": "updateduser",
            "password": "newpassword"
        },
    )
    token = response.json()["access_token"]

    # Now, create a crime
    response = client.post(
        "/crime/crimes",
        json={
            "crime_type": "Theft",
            "description": "Stolen bicycle",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Crime created successfully"
    assert data["crime"][0]["crime_type"] == "Theft"
    assert data["crime"][0]["description"] == "Stolen bicycle"
    assert data["crime"][0]["latitude"] == 40.7128
    assert data["crime"][0]["longitude"] == -74.0060

def test_get_crimes(client):
    response = client.get("/crime/crime")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_get_crime_by_id(client):
    # Assuming the first crime has ID 1
    response = client.get("/crime/crime/1")
    assert response.status_code == 200
    data = response.json()
    assert data["crime_id"] == 1
    assert data["crime_type"] == "Theft"
    assert data["description"] == "Stolen bicycle"
    assert data["latitude"] == 40.7128
    assert data["longitude"] == -74.0060

def test_delete_crime(client):
    # First, login to get a token
    response = client.post(
        "/auth/login",
        data={
            "username": "updateduser",
            "password": "newpassword"
        },
    )
    token = response.json()["access_token"]

    # Now, delete the crime with ID 1
    response = client.delete(
        "/crime/crime/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Crime deleted successfully"

    # Verify the crime is deleted
    response = client.get("/crime/crime/1")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Crime not found"

def test_create_vote_authenticated(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "updateduser",
            "password": "newpassword"
        },
    )
    token = response.json()["access_token"]

    response = client.post(
        "/crime/crimes",
        json={
            "crime_type": "Burglary",
            "description": "House break-in",
            "latitude": 34.0522,
            "longitude": -118.2437
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    crime_id = response.json()["crime"][0]["crime_id"]

    # Now, create a vote for the crime
    response = client.post(
        f"/vote/crimes/{crime_id}/vote",
        json={"vote_type": "up"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["crime_id"] == crime_id
    assert data["vote_type"] == "up"
    assert data["user_id"] is not None


def test_create_vote_anonymous(client):
    response = client.post(
        "/vote/crimes/1/vote",
        json={"vote_type": "down"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["crime_id"] == 1
    assert data["vote_type"] == "down"
    assert data["user_id"] is None

def test_get_votes(client):
    response = client.get("/vote/crimes/1/votes")
    assert response.status_code == 200
    data = response.json()
    assert "authenticated" in data
    assert "anonymous" in data
    assert "total" in data


def test_admin_flag_crime(client):
    # 1. Signup normal user
    response = client.post("/auth/signup", json={
        "email": "user@example.com",
        "username": "normaluser",
        "password": "userpassword",
        "fullname": "Normal User",
        "role": "user"
    })
    assert response.status_code == 200

    # Login as user to create crime
    response = client.post("/auth/login", data={
        "username": "normaluser",
        "password": "userpassword"
    })
    user_token = response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post("/crime/crimes", json={
        "crime_type": "Vandalism",
        "description": "Graffiti on wall",
        "latitude": 51.5074,
        "longitude": -0.1278
    }, headers=user_headers)
    assert response.status_code == 200
    crime_id = response.json()["crime"][0]["crime_id"]

    response = client.post("/auth/signup", json={
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "adminpassword",
        "fullname": "Admin User",
        "role": "admin"
    })
    assert response.status_code == 200

    # Login as admin
    response = client.post("/auth/login", data={
        "username": "adminuser",
        "password": "adminpassword"
    })
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin flags the crime
    response = client.post(f"admin/crime/{crime_id}/flag", json={
        "reason": "Offensive report",
        "is_flagged": True
    }, headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["crime_id"] == crime_id
    assert data["flagged_by"] == 3
    assert data["reason"] == "Offensive report"


def test_admin_get_flagged_crimes(client):
    # Login as admin
    response = client.post("/auth/login", data={
        "username": "adminuser",
        "password": "adminpassword"
    })
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/admin/crimes/flagged", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "reason" in data[0]
    assert "flagged_by" in data[0]

def test_admin_get_statistics(client):
    # Login as admin
    response = client.post("/auth/login", data={
        "username": "adminuser",
        "password": "adminpassword"
    })
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/admin/statistics", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_reports" in data
    assert "top_crime_types" in data
    assert "hotspots" in data


def test_subscribe_alert(client):
    response = client.post("/auth/signup", json={
        "email": "subuser@example.com",
        "username": "subuser",
        "password": "password123",
        "fullname": "Sub Test User",
        "role": "user"
    })
    assert response.status_code == 200

    response = client.post("/auth/login", data={
        "username": "subuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create a subscription
    response = client.post("alerts/subscribe", json={
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius": 10,
        "is_active": True
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] is not None
    assert data["latitude"] == 40.7128
    assert data["longitude"] == -74.0060
    assert data["radius"] == 10
    assert data["is_active"] is True


def test_get_subscription(client):
    response = client.post("/auth/login", data={
        "username": "subuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("alerts/subscribe", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] is not None
    assert data["latitude"] == 40.7128
    assert data["longitude"] == -74.0060
    assert data["radius"] == 10
    assert data["is_active"] is True


def test_create_sos(client):
    response = client.post("/auth/signup", json={
        "email": "sosuser@example.com",
        "username": "sosuser",
        "password": "password123",
        "fullname": "SOS User",
        "role": "user"
    })
    assert response.status_code == 200

    response = client.post("/auth/login", data={
        "username": "sosuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create an SOS report
    response = client.post("/sos/send_sos", json={
            "latitude": 40.7128,
            "longitude": -74.0060,
            "message": "Need help!",
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] is not None
    assert data["latitude"] == 40.7128
    assert data["longitude"] == -74.0060
    assert data["message"] == "Need help!"

def test_get_all_sos_alerts(client):
    response = client.post("/auth/login", data={
        "username": "adminuser",
        "password": "adminpassword"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/sos/sos_alerts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "message" in data[0]
    assert "latitude" in data[0]
    assert "longitude" in data[0]