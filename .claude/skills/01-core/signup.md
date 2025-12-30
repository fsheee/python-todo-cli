---
name: signup
description: Create new user account. Use for user registration.
---

When signing up:

1. **Required**: email, password, name
2. Hash password with bcrypt
3. Create user in database
4. Generate access + refresh tokens

Input:
```typescript
{ email, password, name }
```

Returns user data and tokens.
