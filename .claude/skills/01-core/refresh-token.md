---
name: refresh-token
description: Refresh access token using refresh token. Use when access token expires.
---

When refreshing tokens:

1. **Required**: refresh_token
2. Verify refresh token is valid and not expired
3. Generate new access token

Input:
```typescript
{ refresh_token: string }
```

Returns new access token.
