# ADR-002: Authentication Strategy

**Status:** Accepted
**Date:** 2025-12-11
**Decision Makers:** Claude, User

---

## Context

Need to implement user authentication for the multi-user todo application. Users must be able to register, login, and access only their own tasks.

## Decision

Implement **JWT-based authentication** with:
- Backend handles auth (register, login, logout, session endpoints)
- Password hashing with bcrypt
- JWT tokens with 24-hour expiration
- Token stored in localStorage on frontend
- Authorization header sent with each API request

## Rationale

### Why Backend Auth (not Better Auth service)?
- Simpler architecture - no external auth service dependency
- Full control over user data and auth flow
- Easier to debug and customize
- Single codebase for all auth logic

### Why JWT?
- Stateless - no server-side session storage needed
- Works well with REST APIs
- Can include user claims (id, email, name)
- Industry standard for API authentication

### Why bcrypt?
- Industry-proven password hashing algorithm
- Built-in salt generation
- Configurable work factor for future security

## Implementation

### Backend Endpoints
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - End session (client-side)
- `GET /api/auth/session` - Get current user info

### Token Flow
1. User submits credentials
2. Backend validates and returns JWT
3. Frontend stores token in localStorage
4. Frontend sends token with each request
5. Backend validates token on protected routes

## Consequences

### Positive
- Simple, self-contained auth system
- No external dependencies
- Easy to test and debug
- Works offline (token validation is local)

### Negative
- No token refresh mechanism (user must re-login after 24h)
- Token revocation requires additional implementation
- localStorage is vulnerable to XSS (mitigated by proper CSP)

## Alternatives Considered

1. **Better Auth as separate service** - More complex setup
2. **Session-based auth** - Requires server-side storage
3. **OAuth only** - Removed per user request

---
