import pytest
import json
import os
from fastapi.testclient import TestClient
from main import app, USERS_FILE, users_data, load_users

# Create test client
client = TestClient(app)

# Test data
test_user_data = {
    "name": "Test User",
    "email": "test@example.com",
    "role": "student"
}

test_instructor_data = {
    "name": "Test Instructor",
    "email": "instructor@example.com", 
    "role": "instructor"
}

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Backup original users.json if it exists
    backup_file = f"{USERS_FILE}.backup"
    if os.path.exists(USERS_FILE):
        os.rename(USERS_FILE, backup_file)
    
    # Create test users.json
    test_users = [
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "student"},
        {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "instructor"}
    ]
    with open(USERS_FILE, 'w') as f:
        json.dump(test_users, f)
    
    # Load users for the test
    load_users()
    
    yield
    
    # Cleanup: remove test file and restore backup
    if os.path.exists(USERS_FILE):
        os.remove(USERS_FILE)
    if os.path.exists(backup_file):
        os.rename(backup_file, USERS_FILE)

class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_register_valid_user(self):
        """Test successful user registration"""
        response = client.post("/users/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_user_data["name"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == test_user_data["role"]
        assert data["user_id"] == 3  # Should be next ID after sample data
        assert "message" in data
    
    def test_register_instructor(self):
        """Test registering an instructor"""
        response = client.post("/users/register", json=test_instructor_data)
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "instructor"
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Try to register with existing email
        duplicate_data = {
            "name": "Another Alice",
            "email": "alice@example.com",  # Already exists in test data
            "role": "instructor"
        }
        response = client.post("/users/register", json=duplicate_data)
        assert response.status_code == 400
        assert "User already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self):
        """Test registration with invalid email format"""
        invalid_data = {
            "name": "Invalid User",
            "email": "invalid-email",
            "role": "student"
        }
        response = client.post("/users/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_invalid_role(self):
        """Test registration with invalid role"""
        invalid_role_data = {
            "name": "Invalid Role User",
            "email": "invalidrole@example.com",
            "role": "admin"  # Invalid role
        }
        response = client.post("/users/register", json=invalid_role_data)
        assert response.status_code == 422  # Validation error

class TestUserLogin:
    """Test user login endpoint"""
    
    def test_login_existing_user(self):
        """Test login with existing user"""
        login_data = {"email": "alice@example.com"}
        response = client.post("/users/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "Welcome back, Alice Johnson!" in data["message"]
        assert data["role"] == "student"
    
    def test_login_instructor(self):
        """Test login with instructor account"""
        login_data = {"email": "bob@example.com"}
        response = client.post("/users/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "Welcome back, Bob Smith!" in data["message"]
        assert data["role"] == "instructor"
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {"email": "nonexistent@example.com"}
        response = client.post("/users/login", json=login_data)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_login_invalid_email(self):
        """Test login with invalid email format"""
        login_data = {"email": "invalid-email"}
        response = client.post("/users/login", json=login_data)
        assert response.status_code == 422  # Validation error

class TestUserProfile:
    """Test user profile endpoint"""
    
    def test_get_existing_user_profile(self):
        """Test getting profile of existing user"""
        response = client.get("/users/1/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Alice Johnson"
        assert data["email"] == "alice@example.com"
        assert data["role"] == "student"
    
    def test_get_instructor_profile(self):
        """Test getting profile of instructor"""
        response = client.get("/users/2/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert data["name"] == "Bob Smith"
        assert data["role"] == "instructor"
    
    def test_get_nonexistent_user_profile(self):
        """Test getting profile of non-existent user"""
        response = client.get("/users/999/profile")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_get_profile_invalid_id(self):
        """Test getting profile with invalid ID format"""
        response = client.get("/users/invalid/profile")
        assert response.status_code == 422  # Validation error

class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "LMS User Management API" in data["message"]
        assert "endpoints" in data
        assert data["version"] == "1.0.0"

class TestIntegration:
    """Integration tests for complete user workflows"""
    
    def test_complete_user_workflow(self):
        """Test complete workflow: register -> login -> get profile"""
        # 1. Register a new user
        new_user = {
            "name": "Integration Test User",
            "email": "integration@example.com",
            "role": "student"
        }
        register_response = client.post("/users/register", json=new_user)
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]
        
        # 2. Login with the new user
        login_response = client.post("/users/login", json={"email": new_user["email"]})
        assert login_response.status_code == 200
        assert new_user["name"] in login_response.json()["message"]
        
        # 3. Get user profile
        profile_response = client.get(f"/users/{user_id}/profile")
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["name"] == new_user["name"]
        assert profile_data["email"] == new_user["email"]
        assert profile_data["role"] == new_user["role"]