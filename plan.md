# Plan: Remove Google Authentication Functionality

## Summary

Remove all Google OAuth authentication functionality from the project. The Google OAuth feature is currently defined in specs but has not been implemented yet (Phase 7 tasks T041-T048 are all unchecked).

## Files to Modify

### 1. Spec Files (Remove Google OAuth references)

#### `phase2-web/specs/features/authentication.md`
- Remove User Story US-004: "OAuth Sign In (Google)"
- Remove OAuth Sign In acceptance criteria section (lines ~123-129)
- Remove OAuth Edge Cases table (lines ~170-177)
- Remove API endpoints:
  - `GET /api/auth/oauth/google` (lines ~300-306)
  - `GET /api/auth/oauth/google/callback` (lines ~308-316)
- Remove Google OAuth button from UI Requirements for Sign In Page and Sign Up Page (lines ~430, ~445)

#### `phase2-web/specs/frontend/tasks.md`
- Remove entire Phase 7: Google OAuth section (lines ~134-154)
- Update dependency graph to remove Phase 7
- Update Task Summary table to remove Phase 7 row
- Update Total Tasks count from 50 to 42

#### `phase2-web/specs/ui/components.md`
- Remove OAuthButton component section (lines ~449-467)
- Remove "OAuth buttons" references from SignInForm Fields (line ~422)
- Remove "OAuth buttons" references from SignUpForm Fields (line ~445)

#### `phase2-web/specs/ui/pages.md`
- Remove Google OAuth button from Sign In Page layout (lines ~104-106)
- Remove Google OAuth button from Sign Up Page layout (lines ~166-168)
- Remove "Connected Accounts" / Google section from Settings Page (lines ~460-461)

### 2. No Implementation Files to Change

The Google OAuth implementation was never started - all Phase 7 tasks (T041-T048) are unchecked. The existing auth components (`SignInForm.tsx`, `SignUpForm.tsx`, `auth.ts`, `auth-context.tsx`) do not contain any Google OAuth code.

## Execution Steps

1. Edit `phase2-web/specs/features/authentication.md`:
   - Remove US-004 user story
   - Remove OAuth acceptance criteria
   - Remove OAuth edge cases
   - Remove OAuth API endpoints
   - Remove OAuth button UI references

2. Edit `phase2-web/specs/frontend/tasks.md`:
   - Remove Phase 7 section entirely
   - Update dependency graph
   - Update task summary table
   - Adjust total counts

3. Edit `phase2-web/specs/ui/components.md`:
   - Remove OAuthButton component
   - Remove OAuth button references from SignInForm and SignUpForm

4. Edit `phase2-web/specs/ui/pages.md`:
   - Remove Google button from sign-in page layout
   - Remove Google button from sign-up page layout
   - Remove connected accounts section from settings page

## Impact

- **Spec files**: 4 files modified
- **Implementation files**: 0 files modified (feature was not implemented)
- **No breaking changes**: The feature was never implemented, so no runtime changes

## Notes

This is a spec-driven project per CLAUDE.md - we only modify spec files and let automation handle implementation. Since Google OAuth was never implemented, we only need to remove the planned specifications.


