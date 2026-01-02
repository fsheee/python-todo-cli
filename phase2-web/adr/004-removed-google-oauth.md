# ADR-004: Removal of Google OAuth

**Status:** Accepted
**Date:** 2025-12-11
**Decision Makers:** User

---

## Context

The original specification included Google OAuth as an authentication option (Phase 7 in tasks). User requested removal of all Google OAuth functionality.

## Decision

Remove Google OAuth from:
- Feature specifications
- UI specifications
- Component specifications
- Task lists
- All related implementation plans

## Rationale

- Simplifies authentication flow
- Reduces external dependencies
- Email/password auth is sufficient for MVP
- Can be added back later if needed

## Changes Made

### Specs Updated
1. `specs/features/authentication.md`
   - Removed US-004 (OAuth Sign In with Google)
   - Removed OAuth acceptance criteria
   - Removed OAuth edge cases
   - Removed OAuth API endpoints
   - Removed OAuth UI requirements

2. `specs/frontend/tasks.md`
   - Removed Phase 7 (Google OAuth) entirely
   - Updated task counts: 50 → 42
   - Updated phases: 8 → 7

3. `specs/ui/components.md`
   - Removed OAuthButton component
   - Removed OAuth buttons from form fields

4. `specs/ui/pages.md`
   - Removed Google button from sign-in page
   - Removed Google button from sign-up page
   - Removed Connected Accounts from settings

## Consequences

### Positive
- Simpler codebase
- Faster implementation
- No Google API dependencies
- No OAuth callback handling needed

### Negative
- Users cannot use Google to sign in
- May need to re-add later for enterprise users

## Reversibility

This decision can be reversed by:
1. Restoring the removed spec sections
2. Implementing OAuth endpoints
3. Adding OAuth UI components

---
