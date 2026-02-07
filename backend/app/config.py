# app/config.py
"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "Zero-Touch Onboarding Orchestrator"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./data/onboarding.db"

    # ── Authentication ───────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── AI / LLM ─────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    LLM_PROVIDER: str = "openai"  # "openai", "anthropic", or "groq"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"  # For RAG embeddings (fallback)

    # ── Embeddings (Voyage AI) ───────────────────────────────
    VOYAGE_API_KEY: str = ""
    VOYAGE_EMBEDDING_MODEL: str = "voyage-2"

    # ── Google OAuth ─────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


# Singleton settings instance
settings = Settings()
