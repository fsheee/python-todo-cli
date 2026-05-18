# ADR-2026-04-07: Backend Docker Fix and Chat Routing Resolution

## Status
**Implemented**

## Date
2026-04-07

## Context
During Phase IV deployment on Minikube (Windows), multiple issues were discovered:

1. **Backend crashloop** — `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'` from openai SDK 2.x / httpx incompatibility
2. **Empty `app/models/user.py`** — backend ImportError: `cannot import name 'User' from 'app.models.user'`
3. **Backend Dockerfile** — referenced non-existent `requirements-py313.txt`; multi-stage build's `--prefix=/install` approach failed
4. **`/chat` ingress route conflict** — browser GET `/chat` sent to backend API, returned JSON instead of frontend Next.js page
5. **Frontend button confusion** — "Get Started Free" not shown because user was already authenticated (shows "Go to Chat Board" instead)

## Decisions

### Decision 1: Fix Backend Dockerfile to Use Correct Requirements Path
**What:** Changed `COPY requirements.txt .` to `COPY backend/requirements.txt /app/requirements.txt` in `phase3-chatbot/backend/Dockerfile`.

**Reason:** The build context is `phase3-chatbot/`, not `phase3-chatbot/backend/`. The `requirements.txt` at the context root was 0 bytes. The real file is at `backend/requirements.txt`.

**File:** `phase3-chatbot/backend/Dockerfile`

### Decision 2: Simplify to Single-Stage Docker Build
**What:** Removed multi-stage build (builder + runtime stages) in favor of single-stage build.

**Reason:** The `--prefix=/install` approach in the multi-stage build didn't produce the `/install` directory. Single-stage with direct `pip install` is simpler and more reliable, especially with Docker Hub connectivity issues.

### Decision 3: Restore User Model
**What:** Rewrote `app/models/user.py` with the SQLModel `User` class matching Better Auth schema.

**Reason:** File was completely empty (0 bytes). Backend couldn't start because auth module imports `User` from this file.

**File:** `phase3-chatbot/backend/app/models/user.py`

### Decision 4: Change Backend Chat Prefix to `/api/chat`
**What:** Changed `APIRouter(prefix="/chat")` to `APIRouter(prefix="/api/chat")` in `app/routes/chat.py`. Changed frontend `apiClient.post('/chat')` to `apiClient.post('/api/chat')`.

**Reason:** The ingress `/chat PathType: Prefix` was intercepting ALL `/chat` traffic including browser GET requests for the frontend Next.js page at `/chat`. This caused the frontend chat page to show raw JSON instead of the React UI. By moving the backend API under `/api/chat`, it routes through the existing `/api` catch-all and the frontend's `/chat` page is served correctly.

**Files:**
- `phase3-chatbot/backend/app/routes/chat.py`
- `phase3-chatbot/frontend/src/lib/apiClient.ts`
- `helm/gordon/values.yaml` (removed `/chat` direct route)

### Decision 5: Rebuild Backend Using Existing Cached Base Images
**What:** Used `python:3.11-slim` (already in Minikube cache) via `minikube image build` instead of Docker Hub.

**Reason:** Docker Hub is completely unreachable (DNS resolution fails). All builds must use images already cached in the Minikube docker daemon.

## Consequences
- Backend chat URLs now under `/api/` prefix — consistent with standard convention
- The `/api` ingress catch-all handles all backend API traffic
- Frontend `/chat` page is no longer intercepted by ingress
- "Go to Chat Board" button now navigates to the Next.js chat page correctly

## Image Versions
- `todo-chatbot-backend:v13` — latest deployed (before `/api/chat` change, needs rebuild to v14)
- `todo-chatbot-frontend:v8` — deployed (before `apiClient` fix, needs rebuild)

## Remaining Actions
1. Rebuild backend image (v14+ with `/api/chat` prefix)
2. Rebuild frontend image (apiClient.ts fix)
3. Update `values.yaml` with new tags
4. `helm upgrade gordon ./helm/gordon`
5. Test: navigate to `/chat` page, send a message, verify it routes through `/api/chat`
