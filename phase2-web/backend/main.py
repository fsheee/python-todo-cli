"""FastAPI application entry point for the Todo API."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from db import create_db_and_tables
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup: create database tables (skip on serverless cold start errors)
    try:
        create_db_and_tables()
    except Exception:
        pass  # Tables likely already exist
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Todo API",
    description="Multi-user Todo application REST API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://python-todo-cli-d9n6.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/", tags=["root"])
async def root():
    return {"message": "Backend running on Hugging Face"}

