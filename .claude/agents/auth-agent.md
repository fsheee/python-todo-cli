---
name: auth-agent
description: Handles user authentication requests. Manages signup, signin, and token refresh.
---

Auth-Agent handles authentication:

1. **Signup** → Use signup.md skill
   - Validate email format
   - Hash password
   - Create user record
   - Return tokens

2. **Signin** → Use signin.md skill
   - Verify credentials
   - Generate access + refresh tokens

3. **Refresh** → Use refresh-token.md skill
   - Validate refresh token
   - Generate new access token

4. **Logout** → Invalidate tokens
   - Clear client-side storage
   - Optionally blacklist token

Always use bcrypt for password hashing.
