---
name: verify-jwt
description: Verify JWT token and extract user claims. Use for authentication.
---

When verifying JWT:

1. Extract token from Authorization header (Bearer prefix)
2. Decode using JWT_SECRET
3. Check expiration
4. Return user_id and claims

Input:
```typescript
{ token: string }
```

Returns user_id on success, error on failure.
