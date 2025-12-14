# Todo API Backend

FastAPI backend for the multi-user Todo web application.

## Tech Stack

- **Python 3.13+**
- **FastAPI** - Web framework
- **SQLModel** - ORM (SQLAlchemy + Pydantic)
- **Neon PostgreSQL** - Database
- **JWT** - Authentication with bcrypt password hashing

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
cd phase2-web/backend

# Create virtual environment and install dependencies
uv venv
uv sync
```

### Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters
```

### Run Development Server

```bash
uv run uvicorn main:app --reload --port 8000
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Sign in |
| POST | `/api/auth/logout` | Sign out |
| GET | `/api/auth/session` | Get current user |

### Tasks

All task endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |cla


|--------|----------|-------------|
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks` | List tasks |
| GET | `/api/{user_id}/tasks/{task_id}` | Get task |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Toggle completion |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

## API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── main.py           # FastAPI app entry point
├── db.py             # Database connection
├── models.py         # SQLModel database models
├── schemas.py        # Pydantic request/response schemas
├── auth.py           # JWT verification utilities
├── routes/
│   ├── auth.py       # Authentication endpoints
│   └── tasks.py      # Task CRUD endpoints
├── .env              # Environment variables (not in git)
├── .env.example      # Environment template
├── pyproject.toml    # Project dependencies
└── uv.lock           # Locked dependencies
```

## Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique, indexed |
| hashed_password | VARCHAR | Bcrypt hash |
| name | VARCHAR(255) | Display name |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

### Tasks Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| title | VARCHAR(255) | Task title |
| description | TEXT | Optional description |
| completed | BOOLEAN | Completion status |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

## Authentication Flow

1. User registers with email/password
2. Password hashed with bcrypt
3. JWT token issued (24h expiry)
4. Client stores token in localStorage
5. Token sent with each API request
6. Backend validates token and extracts user ID

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=.
```

## Related Documentation

- [API Specification](../specs/api/rest-endpoints.md)
- [Database Schema](../specs/database/schema.md)
- [Authentication Spec](../specs/features/authentication.md)
- [Task CRUD Spec](../specs/features/task-crud.md)
