# app/main.py
"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings
from app.database import create_tables

# ── Import all routers ──────────────────────────────────────
from app.routers import auth, employees, policies, onboarding, calendar
from app.routers import jurisdictions, documents, approvals, chat, compliance


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

    # Seed jurisdiction templates
    from app.database import SessionLocal
    from app.seeds.jurisdictions import seed_jurisdictions
    from app.seeds.compliance import seed_compliance

    seed_db = SessionLocal()
    try:
        jcount = seed_jurisdictions(seed_db)
        if jcount > 0:
            print(f"✅ Seeded {jcount} jurisdiction templates")
        ccount = seed_compliance(seed_db)
        if ccount > 0:
            print(f"✅ Seeded {ccount} compliance items")
    except Exception as e:
        print(f"⚠️  Seed error (non-fatal): {e}")
    finally:
        seed_db.close()

    # Show AI provider status
    from app.services.llm import _get_provider
    provider = _get_provider()
    if provider == "mock":
        print("🤖 LLM: Mock mode (no API keys set)")
    else:
        print(f"🤖 LLM: Using {provider.upper()}")

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
# Merge default origins with any extra production origins from CORS_ORIGINS_STR
_cors_origins = list(settings.CORS_ORIGINS)
if settings.CORS_ORIGINS_STR:
    _cors_origins.extend([o.strip() for o in settings.CORS_ORIGINS_STR.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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
app.include_router(jurisdictions.router)
app.include_router(documents.router)
app.include_router(approvals.router)
app.include_router(chat.router)
app.include_router(compliance.router)


# ── Root endpoint ───────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    """API health check."""
    from app.services.llm import _get_provider

    provider = _get_provider()
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "ai_provider": provider,
        "ai_status": "live" if provider != "mock" else "mock (no API keys)",
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
