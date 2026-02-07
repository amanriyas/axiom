# ===========================
# Axiom Backend — Dockerfile
# ===========================
# FastAPI + SQLite + ChromaDB

FROM python:3.11-slim

# System dependencies for pymupdf, chromadb (ONNX), and general build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Copy the startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start the application
CMD ["./start.sh"]
