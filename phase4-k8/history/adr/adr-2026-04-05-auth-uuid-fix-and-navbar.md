# ADR-2026-04-05: Auth UUID Fix and Navigation Bar

## Status
**Accepted** (partial - code committed, image rebuild pending)

## Date
2026-04-05

## Context
During Phase IV deployment, user reported two issues:
1. User signup/login fails with error "column id is of type uuid but expression is of type character varying"
2. Login and Signup buttons not visible on the landing page at `todo.local`

## Decisions

### Decision 1: Fix User Model UUID Type
**What:** Changed `id` field in `User` model from `str` to `uuid.UUID` to match Neptune PostgreSQL `uuid` column type.

**File:** `phase3-chatbot/backend/app/models/user.py`
```python
# Before:
id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

# After:
id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
```

**Reason:** The Neptune database schema uses native UUID type for the `id` column, but the application was inserting string representation, causing `DatatypeMismatchError`.

### Decision 2: Pin OpenAI SDK to < 2.0
**What:** Pinned `openai>=1.86.0,<2.0.0` in requirements.txt to fix `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'`.

**File:** `phase3-chatbot/backend/requirements.txt`

**Reason:** openai SDK 2.x passes `proxies` argument to `httpx.AsyncClient`, but the installed `httpx` version doesn't accept it. Downgrading to 1.x avoids the incompatibility.

### Decision 3: Add Landing Navigation Bar
**What:** Created `LandingNav.tsx` component with dedicated "Log in" and "Sign up" buttons in the top navigation bar of the landing page.

**Files:**
- `phase3-chatbot/frontend/src/components/landing/LandingNav.tsx` (new)
- `phase3-chatbot/frontend/src/app/page.tsx` (updated to include navbar)
- `phase3-chatbot/frontend/src/styles/globals.css` (navbar CSS styles)

**Reason:** The previous Hero section only had a single "Get Started Free" button with no persistent navigation. Users couldn't easily find Login/Signup links without scrolling or finding the CTA.

### Decision 4: Use kubectl context `minikube`
**What:** Ensure `kubectl config use-context minikube` is set (not `docker-registry-builders`).

**Reason:** Images are built and stored in the `minikube` profile. The `docker-registry-builders` profile has a separate image store and cannot find the built images, causing `ErrImageNeverPull` errors.

## Consequences
- Code changes are committed and pushed to GitHub (`master` branch)
- Requires image rebuild to deploy (blocked by Docker Hub network connectivity)
- The crash-looping backend pod will resolve once `backend:v11` is built with pinned openai
- The navbar will appear once `frontend:v8` is built
- `gordon` Helm release values need updating for new image tags

## Commits
- `ef0d31c` - fix: auth UUID type mismatch and database connectivity
- `95ec25e` - feat: add landing nav bar with login/signup buttons
- `4e33fdd` - fix: restore backend requirements and pin openai to avoid httpx proxy error

## Remaining Actions
1. Rebuild `frontend:v8` inside Minikube (requires Docker Hub access)
2. Rebuild `backend:v11` inside Minikube (requires Docker Hub access)
3. Update `helm/gordon/values.yaml` with new image tags
4. Run `helm upgrade gordon ./helm/gordon`
