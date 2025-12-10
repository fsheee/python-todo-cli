# Feature Specification: Authentication

> **Feature ID:** AUTH-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

This specification defines user authentication for the multi-user todo web application using Better Auth with JWT-based authentication. The system supports email/password registration and OAuth providers.

---

## User Stories

### US-001: User Registration
**As a** new visitor
**I want to** create an account with my email and password
**So that** I can save and access my tasks across sessions

**Details:**
- Email must be valid and unique
- Password must meet security requirements
- Account is created immediately (no email verification required for MVP)
- User is automatically signed in after registration

---

### US-002: User Sign In
**As a** registered user
**I want to** sign in with my email and password
**So that** I can access my saved tasks

**Details:**
- Credentials are validated against stored data
- JWT token is issued on successful authentication
- Failed attempts are rate-limited
- User is redirected to dashboard after sign in

---

### US-003: User Sign Out
**As a** signed-in user
**I want to** sign out of my account
**So that** I can secure my session on shared devices

**Details:**
- JWT token is invalidated/removed from client
- User is redirected to sign-in page
- Session is terminated on the server

---

### US-004: OAuth Sign In (Google)
**As a** user
**I want to** sign in with my Google account
**So that** I can access the app without creating a new password

**Details:**
- Redirects to Google OAuth consent screen
- Creates new account if email doesn't exist
- Links to existing account if email matches
- Issues JWT token on successful authentication

---

### US-005: Persistent Session
**As a** signed-in user
**I want to** remain signed in across browser sessions
**So that** I don't have to sign in every time I visit

**Details:**
- JWT token stored securely in httpOnly cookie
- Token refresh before expiration
- Session persists until explicit sign out or expiration

---

### US-006: Password Reset
**As a** user who forgot my password
**I want to** reset my password via email
**So that** I can regain access to my account

**Details:**
- User requests reset with email address
- Secure reset link sent to email
- Link expires after 1 hour
- Password updated and all sessions invalidated

---

## Acceptance Criteria

### User Registration
- [ ] Valid email and password creates account and returns 201
- [ ] Duplicate email returns 409 Conflict
- [ ] Invalid email format returns 422 Validation Error
- [ ] Password < 8 characters returns 422 Validation Error
- [ ] Password without uppercase returns 422 Validation Error
- [ ] Password without lowercase returns 422 Validation Error
- [ ] Password without number returns 422 Validation Error
- [ ] Successful registration returns JWT token
- [ ] User record created in database with hashed password
- [ ] Password is never stored in plain text

### User Sign In
- [ ] Valid credentials return 200 with JWT token
- [ ] Invalid email returns 401 Unauthorized
- [ ] Invalid password returns 401 Unauthorized
- [ ] Disabled account returns 403 Forbidden
- [ ] JWT token contains user ID in `sub` claim
- [ ] JWT token has appropriate expiration (24 hours)
- [ ] Session record created in database

### User Sign Out
- [ ] Returns 200 on successful sign out
- [ ] Session record removed from database
- [ ] Subsequent requests with old token return 401
- [ ] Client-side token is cleared

### OAuth Sign In
- [ ] Redirects to provider consent screen
- [ ] Callback creates account if new user
- [ ] Callback links to existing account if email matches
- [ ] Returns JWT token on successful auth
- [ ] Provider tokens stored in accounts table
- [ ] Handles OAuth errors gracefully

### Session Management
- [ ] JWT token validated on each API request
- [ ] Expired tokens return 401 with "Token expired"
- [ ] Malformed tokens return 401 with "Invalid token"
- [ ] Token refresh extends session without re-authentication
- [ ] Multiple concurrent sessions allowed per user

### Password Reset
- [ ] Reset request with valid email returns 200 (even if not found)
- [ ] Reset email sent only if account exists
- [ ] Reset token expires after 1 hour
- [ ] Valid reset token allows password change
- [ ] Expired reset token returns 400 Bad Request
- [ ] Used reset token cannot be reused
- [ ] Password change invalidates all existing sessions

---

## Edge Cases

### Registration Edge Cases
| Case | Expected Behavior |
|------|-------------------|
| Email with uppercase letters | Normalized to lowercase before storage |
| Email with leading/trailing spaces | Trimmed before validation |
| Password exactly 8 characters | Accepted if meets all criteria |
| Unicode characters in password | Accepted |
| Email already registered via OAuth | 409 Conflict with message to sign in via OAuth |
| Concurrent registration same email | First succeeds, second gets 409 |

### Authentication Edge Cases
| Case | Expected Behavior |
|------|-------------------|
| 5 failed login attempts | Account temporarily locked (15 minutes) |
| Login during account lockout | 429 Too Many Requests with retry-after |
| Valid credentials after lockout expires | Success, counter reset |
| Token theft/replay attack | Mitigated by short expiration + refresh |
| Clock skew (client vs server) | 5-minute tolerance on token validation |

### OAuth Edge Cases
| Case | Expected Behavior |
|------|-------------------|
| User denies OAuth consent | Redirect to sign-in with error message |
| OAuth provider unavailable | Show error, suggest email/password |
| Email from OAuth differs from registered | Create new account (no auto-link) |
| OAuth account unlinked then re-linked | New account entry created |

### Session Edge Cases
| Case | Expected Behavior |
|------|-------------------|
| Token expires during active use | 401 returned, client should refresh |
| Refresh token after sign out | 401 Unauthorized |
| Database unavailable during auth | 503 Service Unavailable |
| User deleted while session active | 401 on next request |

---

## API Endpoints

### POST /api/auth/register

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Response: 201 Created**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Errors:** 409 (duplicate), 422 (validation)

---

### POST /api/auth/login

Authenticate with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response: 200 OK**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Errors:** 401 (invalid credentials), 429 (rate limited)

---

### POST /api/auth/logout

End current session.

**Headers:** `Authorization: Bearer <token>`

**Response: 200 OK**
```json
{
  "message": "Successfully signed out"
}
```

---

### GET /api/auth/session

Get current session/user info.

**Headers:** `Authorization: Bearer <token>`

**Response: 200 OK**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "expires_at": "2025-12-11T10:30:00Z"
}
```

**Errors:** 401 (not authenticated)

---

### POST /api/auth/refresh

Refresh JWT token.

**Headers:** `Authorization: Bearer <token>`

**Response: 200 OK**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": "2025-12-11T10:30:00Z"
}
```

---

### GET /api/auth/oauth/google

Initiate Google OAuth flow.

**Response: 302 Redirect** to Google consent screen

---

### GET /api/auth/oauth/google/callback

Handle Google OAuth callback.

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: CSRF state token

**Response: 302 Redirect** to dashboard with token in cookie

---

### POST /api/auth/forgot-password

Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response: 200 OK**
```json
{
  "message": "If an account exists, a reset email has been sent"
}
```

---

### POST /api/auth/reset-password

Reset password with token.

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "password": "NewSecurePass123"
}
```

**Response: 200 OK**
```json
{
  "message": "Password successfully reset"
}
```

**Errors:** 400 (invalid/expired token), 422 (validation)

---

## Security Requirements

### Password Requirements
| Requirement | Rule |
|-------------|------|
| Minimum length | 8 characters |
| Maximum length | 128 characters |
| Uppercase | At least 1 |
| Lowercase | At least 1 |
| Number | At least 1 |
| Special character | Recommended, not required |

### Password Storage
- Algorithm: bcrypt with cost factor 12
- Salt: Automatically generated per password
- Never log or expose passwords

### JWT Configuration
| Setting | Value |
|---------|-------|
| Algorithm | HS256 |
| Secret | `BETTER_AUTH_SECRET` env var (min 32 chars) |
| Expiration | 24 hours |
| Issuer | `todoapp.com` |
| Audience | `todoapp.com` |

### Rate Limiting
| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/auth/login` | 5 attempts | 15 minutes |
| `/api/auth/register` | 3 attempts | 1 hour |
| `/api/auth/forgot-password` | 3 attempts | 1 hour |

### Security Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

## Database Requirements

> **Reference:** See `/specs/database/schema.md`

### Tables Used
- `users` - User accounts
- `sessions` - Active sessions
- `accounts` - OAuth provider links

### Indexes Required
- `idx_users_email` - Fast email lookup for login
- `idx_sessions_token` - Fast token validation
- `idx_sessions_expires_at` - Cleanup expired sessions

---

## UI Requirements

### Sign In Page (`/signin`)
- Email input field with validation
- Password input field with show/hide toggle
- "Sign In" button with loading state
- "Forgot password?" link
- "Sign up" link for new users
- Google OAuth button
- Error messages displayed inline

### Sign Up Page (`/signup`)
- Name input field
- Email input field with validation
- Password input field with requirements indicator
- Password confirmation field
- "Create Account" button with loading state
- "Already have an account?" link
- Google OAuth button
- Terms of service checkbox

### Password Reset Pages
- `/forgot-password` - Email input form
- `/reset-password` - New password form (with token in URL)

### Protected Route Behavior
- Unauthenticated users redirected to `/signin`
- `returnUrl` parameter preserved for post-login redirect
- Loading state while checking authentication

---

## Testing Requirements

### Unit Tests
- [ ] Password hashing produces unique hashes
- [ ] Password verification succeeds for correct password
- [ ] Password verification fails for incorrect password
- [ ] JWT token generation includes correct claims
- [ ] JWT token validation accepts valid tokens
- [ ] JWT token validation rejects expired tokens
- [ ] Email normalization handles edge cases

### Integration Tests
- [ ] Registration creates user and returns token
- [ ] Login with valid credentials returns token
- [ ] Login with invalid credentials returns 401
- [ ] OAuth flow creates/links account correctly
- [ ] Session validation accepts valid tokens
- [ ] Session validation rejects invalid tokens
- [ ] Password reset flow works end-to-end
- [ ] Rate limiting blocks excessive attempts

### E2E Tests
- [ ] User can register via sign-up form
- [ ] User can sign in via sign-in form
- [ ] User can sign in via Google OAuth
- [ ] User can sign out and is redirected
- [ ] User can reset forgotten password
- [ ] Protected pages redirect to sign in
- [ ] User is redirected to original page after sign in

---

## Related Specifications

- `/specs/database/schema.md` - Database schema definitions
- `/specs/api/rest-endpoints.md` - REST API endpoints
- `/specs/features/task-crud.md` - Task CRUD (requires auth)
- `/specs/agents/skills/verify-jwt.md` - JWT verification skill

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
