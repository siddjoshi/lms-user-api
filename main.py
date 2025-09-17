import json
import os
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from email_validator import validate_email, EmailNotValidError

# File path for storing users
USERS_FILE = "users.json"

# Pydantic models
class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    role: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['student', 'instructor']:
            raise ValueError('Role must be either "student" or "instructor"')
        return v

class UserLogin(BaseModel):
    email: EmailStr

class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    role: str

class UserRegistrationResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    message: str

class LoginResponse(BaseModel):
    message: str
    role: str

# Global variable to store users in memory
users_data: List[Dict[str, Any]] = []

def load_users():
    """Load users from JSON file into memory"""
    global users_data
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users_data = json.load(f)
        else:
            users_data = []
    except json.JSONDecodeError:
        users_data = []

def save_users():
    """Save users from memory to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)

def get_next_user_id() -> int:
    """Get the next available user ID"""
    if not users_data:
        return 1
    return max(user['id'] for user in users_data) + 1

def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Find user by email address"""
    return next((user for user in users_data if user['email'] == email), None)

def find_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Find user by ID"""
    return next((user for user in users_data if user['id'] == user_id), None)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    load_users()
    yield
    # Shutdown (if needed)

# Initialize FastAPI app with lifespan
app = FastAPI(title="LMS User Management API", version="1.0.0", lifespan=lifespan)

# API Endpoints

@app.post("/users/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration):
    """
    Register a new user
    - Validates email format
    - Checks for duplicate registrations
    - Assigns incremental user ID
    - Saves to JSON file
    """
    # Check if user already exists
    existing_user = find_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered"
        )
    
    # Create new user
    new_user_id = get_next_user_id()
    new_user = {
        "id": new_user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
    
    # Add to memory and save to file
    users_data.append(new_user)
    save_users()
    
    return UserRegistrationResponse(
        user_id=new_user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        message="User registered successfully"
    )

@app.post("/users/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin):
    """
    Login user with email
    - Returns welcome message with user role if registered
    - Returns error if not registered
    """
    user = find_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return LoginResponse(
        message=f"Welcome back, {user['name']}!",
        role=user['role']
    )

@app.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: int):
    """
    Get user profile by ID
    - Returns user details (id, name, email, role)
    """
    user = find_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile(
        id=user['id'],
        name=user['name'],
        email=user['email'],
        role=user['role']
    )

# Root endpoint for API info
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LMS User Management API",
        "version": "1.0.0",
        "endpoints": {
            "register": "POST /users/register",
            "login": "POST /users/login", 
            "profile": "GET /users/{id}/profile"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)