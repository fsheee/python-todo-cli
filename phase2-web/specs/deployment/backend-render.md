# Backend Deployment Specification: Render

Deploy the FastAPI backend to Render with PostgreSQL and Google OAuth.

---

## 1. Project Setup

### GitHub Repository

| Setting | Value |
|---------|-------|
| Repository | `hackathon-todo` |
| Branch | `main` (or `production`) |
| Auto-Deploy | Enabled on push |

### Monorepo Configuration

| Setting | Value |
|---------|-------|
| Root Directory | `phase2-web/backend` |
| Build Filter | `phase2-web/backend/**` |

### Required Files

Ensure these files exist in `phase2-web/backend/`:

```
phase2-web/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLModel/SQLAlchemy models
│   ├── auth.py              # JWT + Google OAuth logic
│   ├── db.py                # Database connection
│   ├── routes/              # API route handlers
│   │   └── *.py
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── requirements.txt     # Python dependencies
│   ├── pyproject.toml       # Project metadata (optional)
│   └── .env.example         # Environment variable template
├── frontend/
└── specs/
```

### requirements.txt

```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0
httpx>=0.26.0
google-auth>=2.27.0
google-auth-oauthlib>=1.2.0
```

---

## 2. Build & Start Commands

### Render Service Configuration

| Setting | Value |
|---------|-------|
| **Service Type** | Web Service |
| **Runtime** | Python 3 |
| **Python Version** | `3.10` (or `3.11`, `3.12`) |
| **Root Directory** | `phase2-web/backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Auto Deploy Settings

| Setting | Value |
|---------|-------|
| Auto-Deploy | Yes |
| Branch | `main` |
| Build Filters | `phase2-web/backend/**` |
| PR Previews | Optional (enable for staging) |

### Python Version Selection

Set Python version via environment variable or `runtime.txt`:

**Option A: Environment Variable**
```
PYTHON_VERSION=3.10.13
```

**Option B: runtime.txt** (in `phase2-web/backend/`)
```
python-3.10.13
```

---

## 3. Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET` | Secret key for JWT signing (min 32 chars) | `your-super-secret-jwt-key-min-32-chars` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins | `https://your-app.vercel.app,https://yourdomain.com` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `123456789.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-xxxxxxxxxxxxxx` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port (Render provides this) | `10000` |
| `HOST` | Server host | `0.0.0.0` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `info` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRY_HOURS` | Token expiration time | `24` |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL | `https://api.yourdomain.com/auth/google/callback` |

### Setting Environment Variables on Render

**Via Dashboard:**
1. Go to your Web Service → Environment tab
2. Click "Add Environment Variable"
3. Add each variable with its value
4. Click "Save Changes" (triggers redeploy)

**Via render.yaml (Infrastructure as Code):**
```yaml
services:
  - type: web
    name: todo-backend
    runtime: python
    rootDir: phase2-web/backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JWT_SECRET
        sync: false  # Must be set manually (sensitive)
      - key: DATABASE_URL
        sync: false
      - key: CORS_ALLOWED_ORIGINS
        sync: false
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      - key: PYTHON_VERSION
        value: 3.10.13
```

### Environment Variable Template (.env.example)

```bash
# Database (Neon/Supabase PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# CORS (comma-separated origins)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Server (optional - Render provides PORT)
DEBUG=false
LOG_LEVEL=info
```

---

## 4. Health Check

### Endpoint Configuration

| Setting | Value |
|---------|-------|
| **Path** | `/health` |
| **Method** | `GET` |
| **Expected Status** | `200 OK` |
| **Timeout** | 30 seconds |

### Implementation

Add to `main.py`:

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Todo API", version="1.0.0")

@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment platforms.
    Returns service status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "todo-backend"
    }

@app.get("/")
async def root():
    """Root endpoint - redirects to docs or returns API info."""
    return {
        "message": "Todo API",
        "docs": "/docs",
        "health": "/health"
    }
```

### Render Health Check Settings

Configure in Dashboard → Settings → Health & Alerts:

| Setting | Value |
|---------|-------|
| Health Check Path | `/health` |
| Healthcheck Timeout | 30 seconds |

---

## 5. Deployment Checklist

### Before Deploy

- [ ] **Code Ready**
  - [ ] All changes committed and pushed to `main` branch
  - [ ] `requirements.txt` includes all dependencies
  - [ ] `main.py` has FastAPI app instance named `app`
  - [ ] Health check endpoint implemented at `/health`
  - [ ] CORS middleware configured

- [ ] **Database Ready**
  - [ ] Neon/Supabase project created
  - [ ] Database connection string obtained
  - [ ] SSL mode enabled (`?sslmode=require`)
  - [ ] Tables created/migrations run

- [ ] **Google OAuth Ready**
  - [ ] Google Cloud Console project created
  - [ ] OAuth consent screen configured
  - [ ] OAuth 2.0 credentials created
  - [ ] Authorized redirect URIs added:
    - `http://localhost:8000/auth/google/callback` (dev)
    - `https://your-api.onrender.com/auth/google/callback` (prod)

- [ ] **Environment Variables**
  - [ ] `JWT_SECRET` generated (32+ characters)
  - [ ] `DATABASE_URL` set correctly
  - [ ] `CORS_ALLOWED_ORIGINS` includes frontend URL
  - [ ] `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set
  - [ ] All sensitive values are unique per environment

### After Deploy

- [ ] **Verify Deployment**
  - [ ] Build completed successfully (check logs)
  - [ ] Service status is "Live"
  - [ ] No errors in deployment logs

- [ ] **Test Endpoints**
  - [ ] Health check: `GET /health` returns 200
  - [ ] API docs: `GET /docs` loads Swagger UI
  - [ ] Root: `GET /` returns API info

- [ ] **Test Authentication**
  - [ ] Google OAuth flow works end-to-end
  - [ ] JWT tokens are issued correctly
  - [ ] Protected endpoints require valid token
  - [ ] Token refresh works (if implemented)

- [ ] **Test Database**
  - [ ] CRUD operations work
  - [ ] Data persists across requests
  - [ ] No connection timeout errors

- [ ] **Test Integration**
  - [ ] Frontend can reach backend API
  - [ ] CORS allows frontend origin
  - [ ] Auth flow works from frontend

### Verification Commands

```bash
# Health check
curl https://your-api.onrender.com/health

# API docs (should redirect to Swagger)
curl -I https://your-api.onrender.com/docs

# Test CORS preflight
curl -X OPTIONS https://your-api.onrender.com/api/tasks \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Test protected endpoint (should return 401)
curl https://your-api.onrender.com/api/tasks

# Test with auth token
curl https://your-api.onrender.com/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 6. Local Testing Commands

### Development Server (uvicorn)

```bash
cd phase2-web/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with specific log level
uvicorn main:app --reload --log-level debug
```

### Docker Deployment (Optional)

**Dockerfile** (create in `phase2-web/backend/`):

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.dockerignore**:

```
.venv
__pycache__
*.pyc
.env
.git
.pytest_cache
tests/
*.md
```

**Docker Commands**:

```bash
cd phase2-web/backend

# Build image
docker build -t todo-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e JWT_SECRET="your-secret" \
  -e CORS_ALLOWED_ORIGINS="http://localhost:3000" \
  -e GOOGLE_CLIENT_ID="your-client-id" \
  -e GOOGLE_CLIENT_SECRET="your-client-secret" \
  todo-backend

# Run with env file
docker run -p 8000:8000 --env-file .env todo-backend

# View logs
docker logs -f <container_id>

# Stop container
docker stop <container_id>
```

**Docker Compose** (optional - `docker-compose.yml` in `phase2-web/`):

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# Run with docker-compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

---

## 7. Notes & Best Practices

### HTTPS Enforcement

- Render automatically provides HTTPS for all services
- All traffic is encrypted via TLS 1.2+
- HTTP requests are automatically redirected to HTTPS
- No additional configuration required

**Force HTTPS in FastAPI** (optional, for other platforms):

```python
from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Only enable in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### Consistent Secrets

| Secret | Must Match Between |
|--------|-------------------|
| `JWT_SECRET` | Backend ↔ Any service validating tokens |
| `GOOGLE_CLIENT_ID` | Backend ↔ Frontend (if using client-side OAuth) |

**Best Practices:**
- Generate secrets using: `openssl rand -hex 32`
- Never commit secrets to version control
- Use different secrets for dev/staging/production
- Rotate secrets periodically
- Store in environment variables, not code

### Frontend Integration

**CORS Configuration** in `main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Parse allowed origins from environment
origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
origins = [origin.strip() for origin in origins if origin.strip()]

# Fallback for development
if not origins:
    origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Total-Count"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

**Frontend API Client Configuration:**

```typescript
// frontend/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken(); // Get JWT from storage/cookie

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    credentials: 'include', // For cookies if used
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

### Database Connection Best Practices

```python
# db.py
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool settings for serverless
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before use
    pool_recycle=300,        # Recycle connections after 5 minutes
    pool_size=5,             # Maximum pool size
    max_overflow=10,         # Allow 10 additional connections
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

def get_session():
    with Session(engine) as session:
        yield session
```

### Google OAuth Redirect URIs

Configure in Google Cloud Console → APIs & Services → Credentials:

| Environment | Redirect URI |
|-------------|--------------|
| Local Dev | `http://localhost:8000/auth/google/callback` |
| Render | `https://your-api.onrender.com/auth/google/callback` |
| Custom Domain | `https://api.yourdomain.com/auth/google/callback` |

### Render-Specific Notes

- **Cold Starts:** Free tier services spin down after 15 minutes of inactivity. First request may take 30-60 seconds.
- **Upgrade to Paid:** For always-on service, upgrade to paid tier.
- **Static Outbound IP:** Not available on free tier. Use paid tier if needed for IP whitelisting.
- **Logs:** Available for 7 days on free tier, 30 days on paid.
- **Custom Domains:** Supported on all tiers with automatic SSL.

---

## 8. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 502 Bad Gateway | App crashed or not started | Check logs for errors |
| Connection timeout | Database unreachable | Verify `DATABASE_URL`, check Neon status |
| CORS error | Origin not allowed | Add frontend URL to `CORS_ALLOWED_ORIGINS` |
| 401 Unauthorized | Invalid/expired token | Check `JWT_SECRET` matches, verify token |
| OAuth error | Invalid redirect URI | Add URI to Google Console |

### Viewing Logs

```bash
# Via Render Dashboard
# Go to your service → Logs tab

# Recent deployments
# Go to your service → Events tab
```

### Rollback

1. Go to your service → Events tab
2. Find the last working deployment
3. Click "Rollback to this deploy"

---

## References

- [Render Python Docs](https://render.com/docs/deploy-fastapi)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
