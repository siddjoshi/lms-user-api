# LMS User Management API

A FastAPI-based User Management API for Learning Management Systems (LMS).

## Features

- **User Registration** - Register new users with email validation and role assignment
- **User Login** - Authenticate users with email-based login
- **User Profile** - Retrieve user profile information
- **Data Persistence** - Local JSON file storage for user data
- **Input Validation** - Email format validation and role validation
- **Error Handling** - Comprehensive error responses with appropriate HTTP status codes

## API Endpoints

### 1. Register User
**POST** `/users/register`

Register a new user with name, email, and role.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "student"
}
```

**Response (201 Created):**
```json
{
  "user_id": 3,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "student",
  "message": "User registered successfully"
}
```

**Validation Rules:**
- Email must be in valid format
- Role must be either "student" or "instructor"
- Email must be unique (no duplicate registrations)

### 2. Login User
**POST** `/users/login`

Login user with email address.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Welcome back, John Doe!",
  "role": "student"
}
```

### 3. Get User Profile
**GET** `/users/{id}/profile`

Retrieve user profile by user ID.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "student"
}
```

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd lms-user-api
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify sample data:**
The API comes with pre-populated sample users in `users.json`:
- Alice Johnson (alice@example.com) - student
- Bob Smith (bob@example.com) - instructor

## Usage

### Running the API Server

**Start the server:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

**Alternative using uvicorn:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

Once the server is running, you can access:
- **Interactive API Documentation (Swagger UI):** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc
- **API Information:** http://localhost:8000/

### Example Usage with curl

**Register a new user:**
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Smith", "email": "jane@example.com", "role": "instructor"}'
```

**Login user:**
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com"}'
```

**Get user profile:**
```bash
curl -X GET "http://localhost:8000/users/1/profile"
```

## Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- **400 Bad Request** - Invalid email format or duplicate registration
- **404 Not Found** - User not found
- **422 Unprocessable Entity** - Validation errors

**Example Error Response:**
```json
{
  "detail": "User already registered"
}
```

## Running Tests

The project includes comprehensive unit tests covering all endpoints and error cases.

**Run all tests:**
```bash
pytest test_main.py -v
```

**Run specific test classes:**
```bash
pytest test_main.py::TestUserRegistration -v
pytest test_main.py::TestUserLogin -v
pytest test_main.py::TestUserProfile -v
```

## Project Structure

```
lms-user-api/
│
├── main.py           # Main FastAPI application
├── test_main.py      # Unit tests
├── users.json        # User data storage
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Dependencies

- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI applications
- **Pydantic** - Data validation and serialization
- **email-validator** - Email format validation
- **pytest** - Testing framework
- **httpx** - HTTP client for testing

## Data Storage

User data is stored in a local JSON file (`users.json`). The file is automatically:
- Loaded on application startup
- Updated immediately when new users register
- Contains incremental numeric user IDs

## Future Enhancements

This API is designed to be easily extensible. Potential future enhancements include:
- Database integration (PostgreSQL, MongoDB)
- JWT-based authentication
- Password management
- User role permissions
- Course enrollment features
- Admin management endpoints
