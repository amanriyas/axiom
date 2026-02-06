# app/main.py
"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_tables

# ── Import all routers ──────────────────────────────────────
from app.routers import auth, employees, policies, onboarding, calendar


# ── Lifespan (startup / shutdown) ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run on startup: create DB tables, ensure directories exist."""
    # Ensure data directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)

    # Create database tables
    create_tables()
    print("✅ Database tables created")
    print(f"🚀 {settings.APP_NAME} is running")
    print("📄 Test page: http://localhost:8000/test")
    print("📚 API docs:  http://localhost:8000/docs")

    yield  # App runs here

    print("👋 Shutting down...")


# ── Create FastAPI app ──────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered employee onboarding automation platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include routers ─────────────────────────────────────────
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(policies.router)
app.include_router(onboarding.router)
app.include_router(calendar.router)


# ── Root endpoint ───────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """API health check."""
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "test_page": "/test",
    }


# ── Test page endpoint ──────────────────────────────────────
@app.get("/test", tags=["Testing"], response_class=HTMLResponse)
async def test_page():
    """Serve the HTML API testing page."""
    test_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "tests", "test_page.html"
    )
    if os.path.exists(test_file):
        with open(test_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Test page not found</h1><p>Create backend/tests/test_page.html</p>")
