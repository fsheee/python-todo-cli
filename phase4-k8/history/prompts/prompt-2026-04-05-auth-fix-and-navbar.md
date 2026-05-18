# Prompt History: 2026-04-05 - Auth Fix & Landing Navbar

## User Request
Fix two issues:
1. Auth UUID type mismatch causing signup/login failure on `todo.local`
2. Login and Signup buttons not visible on landing page

## Work Done
- Created `LandingNav.tsx` component with Login/Signup buttons
- Fixed User model `id` field from `str` to `uuid.UUID`
- Pinned openai SDK `<2.0.0` to fix httpx `proxies` crash
- All changes committed and pushed to GitHub

## Status
Code done, pending image rebuild (blocked by network)

## Key Details
- kubectl context must be: `minikube` (not `docker-registry-builders`)
- Frontend needs build: `todo-chatbot-frontend:v8`
- Backend needs build: `todo-chatbot-backend:v11`
- Values.yaml tags to update: `frontend.tag: v3` → `v8`, `backend.tag: v10` → `v11`
- After builds: `helm upgrade gordon ./helm/gordon`
