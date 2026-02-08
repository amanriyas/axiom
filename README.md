# Axiom - Zero-Touch Employee Onboarding Platform

An AI-powered platform that automates the entire employee onboarding workflow — from contract generation to calendar scheduling — with zero manual intervention.

## Overview

Axiom streamlines employee onboarding by automatically generating jurisdiction-specific documents, managing approvals, and scheduling orientation events. When a new hire is added, the system triggers a 10-step pipeline that handles everything from parsing employee data to requesting equipment.

### Key Features

- **Automated Document Generation** — Employment contracts, NDAs, equity agreements, and offer letters generated using AI with RAG over company policies
- **Multi-Jurisdiction Support** — Jurisdiction-aware templates for US, UK, UAE, Germany, and Singapore
- **Visual Workflow Pipeline** — Real-time 10-step DAG visualization with status tracking
- **Human Approval Workflow** — Approval gate for document review before sending to employees
- **Policy Chatbot** — RAG-powered Q&A over uploaded company policy documents
- **Compliance Tracking** — Monitor document expirations and certifications with predictive alerts
- **Google Calendar Integration** — Auto-schedule orientation, manager 1:1s, and buddy meetups

## Tech Stack

### Frontend
- **Next.js 16** with App Router
- **React 19** with TypeScript
- **Tailwind CSS 4** for styling
- **shadcn/ui** component library
- **React Flow** (@xyflow/react) for workflow visualization
- **React Hook Form** + **Zod** for form validation

### Backend
- **FastAPI** (Python)
- **SQLAlchemy** with SQLite
- **ChromaDB** for vector storage (RAG)
- **Voyage AI** for embeddings
- **OpenAI / Anthropic** for LLM document generation

## Project Structure

```
axiom/
├── frontend/                    # Next.js application
│   └── src/
│       ├── app/                 # App Router pages
│       │   ├── (auth)/          # Login & signup pages
│       │   └── (dashboard)/     # Protected dashboard pages
│       ├── components/          # React components
│       │   ├── ui/              # shadcn/ui components
│       │   ├── layout/          # Sidebar & top navigation
│       │   └── onboarding/      # Workflow visualization
│       ├── hooks/               # Custom React hooks
│       ├── lib/                 # API client & utilities
│       └── types/               # TypeScript definitions
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── routers/             # API route handlers
│   │   ├── services/            # Business logic
│   │   ├── models.py            # SQLAlchemy models
│   │   └── schemas.py           # Pydantic schemas
│   └── data/                    # SQLite DB & ChromaDB
│
└── CLAUDE.md                    # Development instructions
```

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- API keys for:
  - OpenAI or Anthropic (LLM)
  - Voyage AI (embeddings, optional - has free tier)
  - Google Cloud (Calendar integration, optional)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=sqlite:///./data/onboarding.db
   SECRET_KEY=your-secret-key-here

   # LLM Providers (at least one required)
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key

   # Embeddings (optional, falls back to OpenAI)
   VOYAGE_API_KEY=your-voyage-key

   # Google Calendar (optional)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

## Usage

1. **Create an Account** — Sign up at `/signup`
2. **Add Employees** — Go to Employees page and add manually or upload CSV
3. **Upload Policies** — Upload company policy PDFs for RAG context
4. **Start Onboarding** — Click "Start Workflow" on an employee's onboarding page
5. **Review Documents** — Approve generated documents in the Approvals page
6. **Track Compliance** — Monitor document expirations in Compliance page

## 10-Step Onboarding Pipeline

1. **Parse Data** — Extract and validate employee information
2. **Detect Jurisdiction** — Determine applicable legal jurisdiction
3. **Employment Contract** — Generate jurisdiction-specific contract
4. **NDA** — Generate non-disclosure agreement
5. **Equity Agreement** — Generate equity/stock option agreement
6. **Offer Letter** — Generate formal offer letter
7. **[Approval Gate]** — Human review of all documents
8. **Welcome Email** — Draft personalized welcome email
9. **30-60-90 Plan** — Generate onboarding plan
10. **Schedule Events** — Create calendar events (orientation, 1:1s)

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Deploy to Vercel
```

### Backend (Render)
The backend is deployed on Render. Configuration files included:
- `Dockerfile`
- `start.sh`

## License

MIT
