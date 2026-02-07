#!/bin/bash
# ===========================
# Axiom Backend — Startup Script
# ===========================
# Creates data directories, seeds DB on first run, then starts uvicorn.

set -e

echo "🚀 Starting Axiom Backend..."

# Ensure data directories exist
mkdir -p data/policies

# Seed database on first deploy (if DB doesn't exist yet)
if [ ! -f data/onboarding.db ]; then
    echo "🌱 First deploy — seeding database..."
    python -m scripts.seed_data || echo "⚠️  Seed script failed (non-fatal), continuing..."
fi

echo "🔧 Starting uvicorn on port 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
