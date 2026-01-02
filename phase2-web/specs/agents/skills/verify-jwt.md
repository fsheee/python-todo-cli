# Skill Specification: Verify JWT

> **Skill ID:** SKILL-VERIFY-JWT-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

Atomic skill for verifying JWT tokens and extracting user context. This skill is used by all authenticated endpoints to validate requests.

---

## Skill Configuration

```yaml
skill:
  id: verify-jwt
  name: Verify JWT
  version: 1.0.0
  description: Verify JWT token and extract user context

  type: atomic
  category: security

  requires:
    - jwt_secret
```

---

## Input Schema

```typescript
interface VerifyJWTInput {
  token: string;           // JWT token from Authorization header
  expected_user_id?: string;  // Optional: verify token belongs to this user
}
```

### Token Extraction
Token should be extracted from the `Authorization` header:
```
Authorization: Bearer <token>
```

---

## Output Schema

```typescript
interface VerifyJWTOutput {
  success: boolean;
  user?: {
    id: string;           // User ID from 'sub' claim
    email?: string;       // Email if present in token
    name?: string;        // Name if present in token
  };
  token_info?: {
    issued_at: string;    // ISO 8601
    expires_at: string;   // ISO 8601
    issuer: string;
  };
  error?: {
    code: 'MISSING_TOKEN' | 'INVALID_TOKEN' | 'EXPIRED_TOKEN' | 'USER_MISMATCH';
    message: string;
  };
}
```

---

## Implementation

### Python (FastAPI)

```python
import jwt
from datetime import datetime
from typing import Optional
from config import settings
from schemas import VerifyJWTInput, VerifyJWTOutput

class VerifyJWTSkill:
    """Skill for verifying JWT tokens."""

    def __init__(self):
        self.secret = settings.BETTER_AUTH_SECRET
        self.algorithm = "HS256"
        self.issuer = "todoapp.com"

    async def execute(self, input: VerifyJWTInput) -> VerifyJWTOutput:
        """Execute the verify JWT skill."""

        # Check token presence
        if not input.token:
            return VerifyJWTOutput(
                success=False,
                error={
                    "code": "MISSING_TOKEN",
                    "message": "Authorization token is required"
                }
            )

        try:
            # Decode and verify token
            payload = jwt.decode(
                input.token,
                self.secret,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                options={
                    "require": ["sub", "exp", "iat"],
                    "verify_exp": True,
                    "verify_iss": True
                }
            )

            # Extract user info
            user_id = payload["sub"]

            # Check user ID match if expected
            if input.expected_user_id and user_id != input.expected_user_id:
                return VerifyJWTOutput(
                    success=False,
                    error={
                        "code": "USER_MISMATCH",
                        "message": "Token does not match requested user"
                    }
                )

            return VerifyJWTOutput(
                success=True,
                user={
                    "id": user_id,
                    "email": payload.get("email"),
                    "name": payload.get("name")
                },
                token_info={
                    "issued_at": datetime.fromtimestamp(payload["iat"]).isoformat(),
                    "expires_at": datetime.fromtimestamp(payload["exp"]).isoformat(),
                    "issuer": payload.get("iss", self.issuer)
                }
            )

        except jwt.ExpiredSignatureError:
            return VerifyJWTOutput(
                success=False,
                error={
                    "code": "EXPIRED_TOKEN",
                    "message": "Token has expired"
                }
            )
        except jwt.InvalidTokenError as e:
            return VerifyJWTOutput(
                success=False,
                error={
                    "code": "INVALID_TOKEN",
                    "message": f"Invalid token: {str(e)}"
                }
            )
```

### FastAPI Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """FastAPI dependency for authenticated routes."""

    skill = VerifyJWTSkill()
    result = await skill.execute(VerifyJWTInput(token=credentials.credentials))

    if not result.success:
        status_code = status.HTTP_401_UNAUTHORIZED
        if result.error.code == "USER_MISMATCH":
            status_code = status.HTTP_403_FORBIDDEN

        raise HTTPException(
            status_code=status_code,
            detail=result.error.message,
            headers={"WWW-Authenticate": "Bearer"}
        )

    return result.user
```

---

## JWT Token Structure

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload (Claims)
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440001",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1702209600,
  "exp": 1702296000,
  "iss": "todoapp.com",
  "aud": "todoapp.com"
}
```

### Required Claims
| Claim | Description |
|-------|-------------|
| `sub` | User ID (UUID) |
| `iat` | Issued at timestamp |
| `exp` | Expiration timestamp |

### Optional Claims
| Claim | Description |
|-------|-------------|
| `email` | User's email address |
| `name` | User's display name |
| `iss` | Token issuer |
| `aud` | Token audience |

---

## Behavior

### Verification Steps
1. Check token is present
2. Decode token with secret and algorithm
3. Verify signature is valid
4. Verify token is not expired
5. Verify issuer matches expected
6. Extract user ID from `sub` claim
7. If expected_user_id provided, verify match
8. Return user context

### Error Handling
| Error Code | HTTP Status | Condition |
|------------|-------------|-----------|
| `MISSING_TOKEN` | 401 | No token provided |
| `INVALID_TOKEN` | 401 | Token malformed or signature invalid |
| `EXPIRED_TOKEN` | 401 | Token past expiration |
| `USER_MISMATCH` | 403 | Token user != expected user |

### Clock Skew Tolerance
- 5-minute tolerance for expiration checking
- Handles minor client/server time differences

---

## Security Considerations

### Token Storage
- Client: httpOnly cookie or secure storage
- Never expose in URLs or logs
- Clear on sign out

### Secret Management
- `BETTER_AUTH_SECRET` must be at least 32 characters
- Store in environment variables, not code
- Rotate periodically

### Token Lifetime
- Default: 24 hours
- Refresh tokens for extended sessions
- Invalidate on password change

---

## Testing

### Unit Tests

```python
def test_verify_valid_token():
    """Valid token returns user context."""
    token = create_test_token(user_id="test-user-id")
    result = skill.execute(VerifyJWTInput(token=token))

    assert result.success is True
    assert result.user.id == "test-user-id"

def test_verify_missing_token():
    """Missing token returns MISSING_TOKEN error."""
    result = skill.execute(VerifyJWTInput(token=""))

    assert result.success is False
    assert result.error.code == "MISSING_TOKEN"

def test_verify_expired_token():
    """Expired token returns EXPIRED_TOKEN error."""
    token = create_test_token(user_id="test-user-id", expired=True)
    result = skill.execute(VerifyJWTInput(token=token))

    assert result.success is False
    assert result.error.code == "EXPIRED_TOKEN"

def test_verify_invalid_signature():
    """Token with wrong signature returns INVALID_TOKEN error."""
    token = create_test_token(user_id="test-user-id", wrong_secret=True)
    result = skill.execute(VerifyJWTInput(token=token))

    assert result.success is False
    assert result.error.code == "INVALID_TOKEN"

def test_verify_malformed_token():
    """Malformed token returns INVALID_TOKEN error."""
    result = skill.execute(VerifyJWTInput(token="not.a.valid.token"))

    assert result.success is False
    assert result.error.code == "INVALID_TOKEN"

def test_verify_user_mismatch():
    """Token for different user returns USER_MISMATCH error."""
    token = create_test_token(user_id="user-a")
    result = skill.execute(VerifyJWTInput(
        token=token,
        expected_user_id="user-b"
    ))

    assert result.success is False
    assert result.error.code == "USER_MISMATCH"

def test_verify_extracts_optional_claims():
    """Optional claims are extracted when present."""
    token = create_test_token(
        user_id="test-user-id",
        email="user@example.com",
        name="Test User"
    )
    result = skill.execute(VerifyJWTInput(token=token))

    assert result.user.email == "user@example.com"
    assert result.user.name == "Test User"
```

---

## Related Specifications

- `/specs/features/authentication.md` - Authentication feature spec
- `/specs/agents/todo-agent.md` - Uses this skill for auth
- `/specs/api/rest-endpoints.md` - All endpoints require JWT

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
