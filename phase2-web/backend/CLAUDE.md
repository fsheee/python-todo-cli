


### **backend.md** 

```markdown
# Backend Guidelines - Todo Full-Stack Web App

## Purpose
Defines backend patterns, stack, and conventions for the Todo web application (Phase II).

## Tech Stack
- Python 3.13+
- FastAPI
- SQLModel (ORM)
- Neon PostgreSQL
- Pydantic for request/response models
- **Authentication:** Better Auth with JWT tokens

## Folder Structure
- `/backend/main.py` - FastAPI entry point
- `/backend/models.py` - SQLModel database models
- `/backend/routes/` - API route handlers
- `/backend/db.py` - Database connection and session
- `/backend/schemas.py` - Pydantic schemas

## API Conventions
- All endpoints under `/api/{user_id}/...`
- Verify JWT token from Better Auth on each request
- Extract user ID from token and match with route parameter
- Reject requests without valid token (401 Unauthorized)
- Return JSON responses with proper HTTP status codes
- Filter all task operations by authenticated user

## Database Guidelines
- Tasks table columns: id, user_id, title, description, completed, created_at, updated_at
- Users table managed by Better Auth
- Use SQLModel session to create/read/update/delete objects
- Commit transactions after changes
- Refresh objects after update for latest state

## Business Logic
- Keep route functions thin; implement logic in **service functions** if complex
- Validate input data using Pydantic schemas
- Raise `HTTPException` for errors (404, 401, 400)
- Only allow access to user-owned tasks

## JWT / Auth
- Verify JWT token on each request
- Decode token to get user ID
- Match user ID with route parameter
- Reject requests without valid token
- Ensure token expiry and revocation handling

## Claude Code Instructions
- Implement features strictly from `/specs/features/`
- Use atomic skill approach: one API route per atomic task feature
- Reference database schema spec for field types
- Implement REST endpoints only, no frontend logic
- Integrate Better Auth flow for authentication and authorization
