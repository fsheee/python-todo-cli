"""
Main FastAPI application for Phase 3 Chatbot

Spec Reference: specs/overview.md
Python 3.13 Compatible Version
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
# Always load from the Phase 3 project root so running from repo root still works.
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# Python 3.13 SQLAlchemy workaround
if sys.version_info >= (3, 13):
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*TypingOnly.*")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    logger.info("🚀 Phase 3 Chatbot starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Initialize database (skip if fails due to Python 3.13 issues)
    try:
        from app.database import init_db
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization skipped: {e}")
        logger.info("📝 Using file-based storage as fallback")

    # Create data directories for file storage
    os.makedirs("data/chat-history", exist_ok=True)
    logger.info("✅ File storage ready")

    yield

    # Shutdown
    logger.info("🛑 Phase 3 Chatbot shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Todo Chatbot API",
    description="AI-powered conversational todo management (Phase 3)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
# Get allowed origins from environment variable or use defaults
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,https://todo-app-chatbot.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
try:
    from app.middleware.rate_limit import add_rate_limit_middleware
    add_rate_limit_middleware(app)
    logger.info("✅ Rate limiting enabled (30 requests/minute)")
except Exception as e:
    logger.warning(f"⚠️ Rate limiting not loaded: {e}")

# Include routers
from app.routes.auth import router as auth_router
app.include_router(auth_router)
logger.info("✅ Auth router loaded")

try:
    from app.router import process_chat_message  # Import the agent function
    from app.routes.chat import router as chat_router
    app.include_router(chat_router)
    logger.info("✅ Chat router loaded")
except ImportError as e:
    logger.warning(f"⚠️ Chat router not loaded: {e}")

try:
    from app.routes.history import router as history_router
    app.include_router(history_router)
    logger.info("✅ History router loaded")
except ImportError as e:
    logger.warning(f"⚠️ History router not loaded: {e}")

try:
    from app.routes.prompts import router as prompts_router
    app.include_router(prompts_router)
    logger.info("✅ Prompts router loaded")
except ImportError as e:
    logger.warning(f"⚠️ Prompts router not loaded: {e}")

try:
    from app.routes.tasks import router as tasks_router
    app.include_router(tasks_router)
    logger.info("✅ Tasks router loaded")
except ImportError as e:
    logger.warning(f"⚠️ Tasks router not loaded: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Todo Chatbot API - Phase 3",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            "", 0, "", 0, "", (), None
        ))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
