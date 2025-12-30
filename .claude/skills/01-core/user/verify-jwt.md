# Skill Specification: Verify JWT

> **Skill ID:** SKILL-VERIFY-JWT-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Security skill for validating JWT tokens. This skill verifies the authenticity and validity of JWT tokens issued by Better Auth. Returns user_id and claims if valid, error if invalid.

---

## Skill Configuration

```yaml
skill:
  id: verify-jwt
  name: Verify JWT
  version: 1.0.0
  description: Validate JWT token and extract user claims

  # Skill type
  type: atomic
  category: auth

  # Dependencies
  requires:
    - jwt_secret
```

---

## Input Schema

```typescript
interface VerifyJWTInput {
  token: string;             // JWT token string (Bearer token)
}
```

### Validation Rules

| Field | Rule | Error Message | Default |
|-------|------|---------------|---------|
| `token` | Required | "Token is required" | - |
| `token` | Valid JWT format | "Invalid token format" | - |

---

## Output Schema

```typescript
interface VerifyJWTOutput {
  success: boolean;
  user_id?: string;          // UUID of authenticated user
  claims?: {
    email?: string;
    name?: string;
    exp?: number;            // Expiration timestamp
    iat?: number;            // Issued at timestamp
  };
  error?: {
    code: string;
    message: string;
  };
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `INVALID_TOKEN` | Token is malformed or invalid |
| `TOKEN_EXPIRED` | Token has expired |
| `MISSING_TOKEN` | Token is missing |

---

## Implementation

### Python (Better Auth)

```python
from datetime import datetime, timezone
from jose import jwt, JWTError
from pydantic import BaseModel

class VerifyJWTInput(BaseModel):
    token: str

class VerifyJWTOutput(BaseModel):
    success: bool
    user_id: str | None = None
    claims: dict | None = None
    error: dict | None = None

class VerifyJWTSkill:
    """Skill for verifying JWT tokens."""

    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret

    async def execute(self, input: VerifyJWTInput) -> VerifyJWTOutput:
        """Execute the verify JWT skill."""

        # Validate input
        if not input.token:
            return VerifyJWTOutput(
                success=False,
                error={
                    "code": "MISSING_TOKEN",
                    "message": "Token is required"
                }
            )

        # Remove Bearer prefix if present
        token = input.token
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            # Decode and verify JWT
            claims = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )

            # Extract user_id
            user_id = claims.get("sub") or claims.get("user_id")
            if not user_id:
                return VerifyJWTOutput(
                    success=False,
                    error={
                        "code": "INVALID_TOKEN",
                        "message": "Token missing user identifier"
                    }
                )

            # Check expiration
            exp = claims.get("exp")
            if exp:
                exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
                if exp_dt < datetime.now(timezone.utc):
                    return VerifyJWTOutput(
                        success=False,
                        error={
                            "code": "TOKEN_EXPIRED",
                            "message": "Token has expired"
                        }
                    )

            return VerifyJWTOutput(
                success=True,
                user_id=user_id,
                claims={
                    "email": claims.get("email"),
                    "name": claims.get("name"),
                    "exp": exp,
                    "iat": claims.get("iat")
                }
            )

        except jwt.ExpiredSignatureError:
            return VerifyJWTOutput(
                success=False,
                error={
                    "code": "TOKEN_EXPIRED",
                    "message": "Token has expired"
                }
            )
        except JWTError as e:
            return VerifyJWTOutput(
                success=False,
                error={
                    "code": "INVALID_TOKEN",
                    "message": f"Invalid token: {str(e)}"
                }
            )
```

---

## Behavior

### Success Flow

```
1. Receive token string
2. Remove "Bearer " prefix if present
3. Decode JWT with HS256 algorithm
4. Verify signature using jwt_secret
5. Check expiration claim
6. Extract user_id from claims
7. Return success with user_id and claims
```

### Error Flow

```
1. Missing token → MISSING_TOKEN error
2. Invalid format → INVALID_TOKEN error
3. Expired token → TOKEN_EXPIRED error
4. Invalid signature → INVALID_TOKEN error
5. Missing user_id → INVALID_TOKEN error
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| No database | Read-only verification |
| No state change | Stateless operation |

---

## Idempotency

**This skill is idempotent.** Same token returns same result (until expiration).

---

## Reuse Across Phases

### Phase 2 (Web Backend)

- Used by FastAPI dependencies for all protected endpoints
- Called before executing any skill that requires user_context

### Phase 3 (Chatbot)

- Used at connection time to validate user session
- User_id extracted and passed to all subsequent MCP calls

### Reused Components

- JWT decoding logic (shared across phases)
- Error handling (consistent)
- Claims extraction (standardized)

---

## Testing

### Unit Tests

```python
def test_verify_jwt_success():
    """Valid token returns user claims."""
    # Create a valid token
    token = create_test_jwt(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        email="test@example.com"
    )

    input = VerifyJWTInput(token=token)
    result = skill.execute(input)

    assert result.success is True
    assert result.user_id == "550e8400-e29b-41d4-a716-446655440001"
    assert result.claims.email == "test@example.com"

def test_verify_jwt_missing():
    """Missing token returns error."""
    input = VerifyJWTInput(token="")
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "MISSING_TOKEN"

def test_verify_jwt_expired():
    """Expired token returns error."""
    # Create an expired token
    token = create_expired_jwt(
        user_id="550e8400-e29b-41d4-a716-446655440001"
    )

    input = VerifyJWTInput(token=token)
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "TOKEN_EXPIRED"

def test_verify_jwt_invalid():
    """Invalid token returns error."""
    input = VerifyJWTInput(token="invalid.token.here")
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "INVALID_TOKEN"
```

---

## Related Specifications

- `/specs/features/authentication.md` - Authentication feature
- `/specs/agents/todo-agent.md` - Parent agent
- `/specs/database/schema.md` - User schema

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-10 | Claude | Initial specification |
| 1.0.0 | 2025-12-31 | Claude | Updated with Phase 3 integration |
