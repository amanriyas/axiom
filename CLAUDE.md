# CLAUDE.md — Zero-Touch Onboarding Orchestrator

## Project Overview

This is a hackathon project building an AI-powered zero-touch onboarding platform. The system automates the entire employee onboarding workflow — from contract generation to calendar scheduling — with zero manual intervention.

**Core Value Proposition:** New hire acceptance triggers automatic contract generation, system provisioning, and scheduling with zero manual work.

---

## 📚 Documentation Links — ALWAYS REFERENCE THESE

When writing code, actively consult these official docs to ensure up-to-date patterns and avoid deprecated APIs.

### Frontend Documentation

| Library | Docs URL | Use For |
|---------|----------|---------|
| **Next.js 15** | https://nextjs.org/docs | App Router, Server Components, API Routes |
| **React 18** | https://react.dev/reference/react | Hooks, Components, Patterns |
| **shadcn/ui** | https://ui.shadcn.com/docs | Component usage, installation, theming |
| **Tailwind CSS** | https://tailwindcss.com/docs | Utility classes, configuration |
| **React Flow** | https://reactflow.dev/docs | Workflow visualization, nodes, edges |
| **NextAuth.js** | https://next-auth.js.org/getting-started/introduction | Authentication, providers, sessions |
| **Lucide Icons** | https://lucide.dev/icons | Icon search and usage |
| **React Dropzone** | https://react-dropzone.js.org | File upload handling |
| **Zod** | https://zod.dev | Schema validation |
| **TypeScript** | https://www.typescriptlang.org/docs | Type system reference |

### Backend Documentation

| Library | Docs URL | Use For |
|---------|----------|---------|
| **FastAPI** | https://fastapi.tiangolo.com | Routes, dependencies, middleware |
| **SQLAlchemy 2.0** | https://docs.sqlalchemy.org/en/20 | ORM, queries, relationships |
| **Pydantic V2** | https://docs.pydantic.dev/latest | Schemas, validation, settings |
| **ChromaDB** | https://docs.trychroma.com | Vector store, embeddings, queries |
| **LangChain** | https://python.langchain.com/docs | RAG, chains, document loaders |
| **OpenAI Python** | https://platform.openai.com/docs/api-reference | API calls, embeddings, chat |
| **Anthropic Python** | https://docs.anthropic.com/en/api | Claude API integration |
| **Voyage AI** | https://docs.voyageai.com | Embeddings (50M free tokens) |
| **PyMuPDF** | https://pymupdf.readthedocs.io/en/latest | PDF text extraction |
| **Pandas** | https://pandas.pydata.org/docs | CSV parsing, data manipulation |
| **Python-Jose** | https://python-jose.readthedocs.io/en/latest | JWT encoding/decoding |
| **Passlib** | https://passlib.readthedocs.io/en/stable | Password hashing |

### Google APIs Documentation

| API | Docs URL | Use For |
|-----|----------|---------|
| **Google Calendar API** | https://developers.google.com/calendar/api/guides/overview | Event creation, OAuth |
| **Google Auth Library** | https://google-auth.readthedocs.io/en/latest | OAuth2 authentication |

### Deployment Documentation

| Platform | Docs URL | Use For |
|----------|----------|---------|
| **Vercel** | https://vercel.com/docs | Frontend deployment |
| **Railway** | https://docs.railway.app | Backend deployment |

---

## Important Notes for Claude Code

### ⚠️ Manual Code Changes
The developer may manually modify code at any time. Always:
- Check the current state of files before making assumptions
- Do not overwrite manual changes without confirmation
- Ask before refactoring existing code structures
- Preserve comments marked with `// MANUAL:` or `# MANUAL:`

### Development Approach
1. **Frontend-first development** — Build and validate UI before backend integration
2. **Incremental building** — Small, testable chunks
3. **Design will evolve** — Frontend layout is intentionally ambiguous; screenshots will be provided later for reference

---

## Tech Stack

### Frontend
- **Framework:** Next.js 15 (App Router) — [Docs](https://nextjs.org/docs)
- **UI Library:** shadcn/ui (MUST USE for all components) — [Docs](https://ui.shadcn.com/docs)
- **Styling:** Tailwind CSS — [Docs](https://tailwindcss.com/docs)
- **State Management:** React hooks + Context (no Redux)
- **Visualization:** React Flow (for workflow graph) — [Docs](https://reactflow.dev/docs)
- **Deployment:** Vercel — [Docs](https://vercel.com/docs)

### Backend
- **Framework:** FastAPI — [Docs](https://fastapi.tiangolo.com)
- **Database:** SQLite with SQLAlchemy ORM — [Docs](https://docs.sqlalchemy.org/en/20)
- **Vector Store:** ChromaDB (for RAG) — [Docs](https://docs.trychroma.com)
- **Embeddings:** Voyage AI (primary, 50M free tokens) — [Docs](https://docs.voyageai.com)
- **LLM:** OpenAI GPT-4 / Claude API — [OpenAI Docs](https://platform.openai.com/docs) | [Anthropic Docs](https://docs.anthropic.com)
- **Authentication:** Google OAuth + Email/Password
- **Deployment:** Railway — [Docs](https://docs.railway.app)

---

## Project Structure

```
zero-touch-onboarding/
├── frontend/                    # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Landing + upload
│   │   │   ├── layout.tsx           # Root layout
│   │   │   ├── providers.tsx        # Client providers
│   │   │   ├── globals.css          # Global styles
│   │   │   ├── (auth)/              # Auth routes group
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── signup/page.tsx
│   │   │   └── (dashboard)/         # Dashboard route group
│   │   │       ├── layout.tsx
│   │   │       ├── dashboard/page.tsx       # Main dashboard
│   │   │       ├── employees/page.tsx       # Employee management + jurisdiction
│   │   │       ├── onboarding/page.tsx      # Onboarding list
│   │   │       │   └── [id]/page.tsx        # Workflow visualizer (10 steps)
│   │   │       ├── policies/page.tsx        # Policy document manager
│   │   │       ├── approvals/page.tsx       # Document approval workflow ★ NEW
│   │   │       ├── chat/page.tsx            # Policy chatbot ★ NEW
│   │   │       ├── compliance/page.tsx      # Compliance tracking ★ NEW
│   │   │       └── settings/page.tsx        # App settings + OAuth
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn/ui components (20+)
│   │   │   ├── layout/
│   │   │   │   ├── sidebar.tsx      # Navigation with dynamic badges
│   │   │   │   └── top-nav.tsx      # Top navigation bar
│   │   │   └── onboarding/
│   │   │       ├── workflow-graph.tsx  # 10-step DAG with approval gate
│   │   │       ├── workflow-node.tsx   # Custom node with 10 step icons
│   │   │       └── index.ts
│   │   ├── lib/
│   │   │   ├── api.ts               # API client (9 namespaces)
│   │   │   └── utils.ts             # General utilities
│   │   ├── hooks/
│   │   │   ├── use-auth.tsx         # Auth hook
│   │   │   └── use-sse-stream.ts    # SSE streaming hook
│   │   └── types/
│   │       └── index.ts             # All TypeScript types
│   └── public/                  # Static assets
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py              # FastAPI entry point (10 routers, startup seeds)
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models (19 classes)
│   │   ├── schemas.py           # Pydantic V2 schemas
│   │   ├── routers/
│   │   │   ├── auth.py          # Authentication routes
│   │   │   ├── employees.py     # Employee CRUD
│   │   │   ├── policies.py      # Policy management + RAG upload
│   │   │   ├── onboarding.py    # Onboarding orchestration + SSE
│   │   │   ├── calendar.py      # Google Calendar integration
│   │   │   ├── jurisdictions.py # Jurisdiction templates ★ NEW
│   │   │   ├── documents.py     # Generated documents ★ NEW
│   │   │   ├── approvals.py     # Approval workflow ★ NEW
│   │   │   ├── chat.py          # Policy chatbot ★ NEW
│   │   │   └── compliance.py    # Compliance tracking ★ NEW
│   │   ├── services/
│   │   │   ├── auth.py          # Auth service
│   │   │   ├── orchestrator.py  # Workflow engine (10-step pipeline)
│   │   │   ├── rag.py           # RAG engine
│   │   │   ├── llm.py           # Multi-provider LLM (Groq→OpenAI→Anthropic→Mock)
│   │   │   ├── embeddings.py    # Voyage AI embedding provider
│   │   │   ├── employee.py      # Employee service
│   │   │   ├── policy.py        # Policy service
│   │   │   ├── calendar.py      # Calendar service
│   │   │   ├── document_generator.py  # Jurisdiction-aware doc gen ★ NEW
│   │   │   ├── approval.py      # Approval workflow service ★ NEW
│   │   │   ├── chat.py          # RAG chatbot service ★ NEW
│   │   │   └── compliance.py    # Compliance tracking service ★ NEW
│   │   ├── prompts/
│   │   │   ├── templates.py     # Core prompt templates
│   │   │   └── documents/       # Document-specific prompts ★ NEW
│   │   │       ├── employment_contract.py
│   │   │       ├── nda.py
│   │   │       ├── equity_agreement.py
│   │   │       └── offer_letter.py
│   │   └── seeds/               # Database seed data ★ NEW
│   │       ├── jurisdictions.py # 3 jurisdictions × 3 templates
│   │       └── compliance.py    # Sample compliance items
│   ├── data/
│   │   ├── onboarding.db        # SQLite database
│   │   ├── chromadb/            # ChromaDB vector store
│   │   ├── policies/            # Uploaded policy PDFs
│   │   └── template_overrides.json
│   ├── scripts/
│   │   └── seed_data.py         # Manual seed script
│   ├── tests/
│   │   ├── test_page.html       # HTML page for manual API testing
│   │   └── test_embeddings.py
│   └── requirements.txt
│
├── CLAUDE.md                    # This file
├── COPILOT.md                   # GitHub Copilot instructions
└── README.md                    # Project README
```

---

## Frontend Dependencies

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.331.0",
    "next-auth": "^5.0.0-beta.0",
    "next-themes": "^0.2.1",
    "@xyflow/react": "^12.0.0",
    "react-dropzone": "^14.2.3",
    "tailwind-merge": "^2.2.1",
    "tailwindcss-animate": "^1.0.7",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/node": "^20.11.16",
    "@types/react": "^18.2.52",
    "@types/react-dom": "^18.2.18",
    "autoprefixer": "^10.4.17",
    "eslint": "^8.56.0",
    "eslint-config-next": "^15.0.0",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3"
  }
}
```

> **Note:** React Flow has been renamed to `@xyflow/react` in v12+. See [migration guide](https://reactflow.dev/learn/troubleshooting/migrate-to-v12).

### shadcn/ui Components to Install
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input label select textarea
npx shadcn-ui@latest add dialog alert-dialog dropdown-menu
npx shadcn-ui@latest add table tabs toast avatar badge
npx shadcn-ui@latest add form separator skeleton progress
```

---

## Backend Dependencies

```txt
# requirements.txt

# Core
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9

# Database
sqlalchemy==2.0.25
aiosqlite==0.19.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
google-auth==2.27.0
google-auth-oauthlib==1.2.0

# AI/ML
openai==1.12.0
anthropic==0.18.1
chromadb==0.4.22
voyageai==0.2.1
langchain-voyageai==0.1.0
langchain==0.1.6
langchain-openai==0.0.5

# Document Processing
pandas==2.2.0
pymupdf==1.23.22
python-docx==1.1.0

# Google APIs
google-api-python-client==2.118.0
google-auth-httplib2==0.2.0

# Utilities
python-dotenv==1.0.1
pydantic==2.6.1
pydantic-settings==2.1.0
httpx==0.26.0

# Development
pytest==8.0.0
pytest-asyncio==0.23.4
```

---

## Authentication Requirements

### Google OAuth Sign-In
- Use NextAuth.js on frontend
- Backend validates Google tokens
- Store user in database on first login

### Email/Password Sign-In
- bcrypt for password hashing
- JWT tokens for session management
- Refresh token rotation

### Auth Flow
```
Frontend (NextAuth) → Backend (/api/auth/*) → Database
                   ↓
            Google OAuth Provider
```

---

## Key Features

### 1. Visual Workflow Graph (React Flow) ✅
- **10-step pipeline**: Parse Data → Detect Jurisdiction → Employment Contract → NDA → Equity Agreement → Offer Letter → **[APPROVAL GATE]** → Welcome Email → 30-60-90 Plan → Schedule Events → Equipment Request
- Real-time status updates (pending, running, completed, failed, awaiting_approval)
- Animated transitions between states
- Approval gate visualization on edges between document generation and post-approval steps

### 2. RAG for Policies ✅
- Upload PDF policy documents
- Chunk and embed with Voyage AI embeddings (primary) or OpenAI (fallback)
- Store in ChromaDB
- Retrieve relevant context for document generation

### Embedding Provider
- **Primary:** Voyage AI (`voyage-2` model) — [Docs](https://docs.voyageai.com/)
- **Fallback:** OpenAI (`text-embedding-3-small`) → ChromaDB default (sentence-transformer)
- Voyage AI offers **50M free tokens** with no credit card required
- Get API key at https://www.voyageai.com/
- Set `VOYAGE_API_KEY` in `.env` to activate

### 3. Agent Thinking Panel ✅
- Server-Sent Events (SSE) for streaming
- Display AI reasoning in real-time
- Auto-scroll as new content arrives

### 4. File Upload ✅
- CSV: Employee roster bulk import
- PDF: Policy documents for RAG

### 5. Google Calendar Integration ✅
- OAuth flow for calendar access
- Auto-schedule: Orientation, Manager 1:1, Buddy meetup
- Mock mode fallback for demos

### 6. Jurisdiction Selector & Multi-Country Support ✅ NEW
- Employee jurisdiction field (US, UK, AE, DE, SG)
- Auto-detection step in pipeline based on employee data
- Jurisdiction-specific document templates (employment contracts, NDAs, equity agreements)
- `JurisdictionTemplate` model stores per-jurisdiction clause templates
- Seeds: 3 jurisdictions (US, UK, AE) × 3 document types = 9 templates

### 7. Expanded Document Generation ✅ NEW
- 4 document types generated per onboarding: Employment Contract, NDA, Equity Agreement, Offer Letter
- Jurisdiction-aware prompt templates in `prompts/documents/`
- `GeneratedDocument` model tracks document status (draft, pending_review, approved, rejected, revision_requested)
- Document download endpoint
- `document_generator.py` service with dedicated functions per document type

### 8. Human Approval Workflow ✅ NEW
- Approval gate inserted after offer_letter step in the pipeline
- Workflow transitions to `AWAITING_APPROVAL` status when gate is reached
- `ApprovalRequest` model tracks individual document approvals
- Approve/Reject/Request Revision actions with notes
- Auto-resume: when all approvals are processed, workflow continues to welcome_email
- SSE emits `approval_gate` event type for real-time frontend updates
- Frontend approvals page with Pending/History tabs and review dialog

### 9. Policy Chatbot ✅ NEW
- RAG-powered Q&A over uploaded policy documents
- Conversation history tracking (`ChatConversation`, `ChatMessage` models)
- SSE streaming for real-time responses
- Source document references displayed as badges
- Suggestion buttons for common questions
- Frontend chat page with conversation sidebar and message UI

### 10. Compliance Tracking & Predictive Alerts ✅ NEW
- `ComplianceItem` model tracks document expiry, training, certifications
- Status tracking: valid, expiring_soon, expired, pending
- Summary endpoint with overall compliance rate calculation
- Predictive alerts based on expiry dates and risk levels
- Frontend compliance page with stats, progress bar, All Items/Alerts/Predictions tabs

---

## Database Models (19 total)

### Core Models
- `User` — Authentication (email, hashed_password, google_id)
- `Employee` — Employee data (name, email, role, department, start_date, **jurisdiction**)
- `OnboardingWorkflow` — Workflow state machine (status includes **awaiting_approval**)
- `OnboardingStep` — Individual step tracking (10 step types, **requires_approval**, **approval_status**)
- `PolicyDocument` — Uploaded policy PDFs for RAG

### New Models (Feature Extensions)
- `JurisdictionTemplate` — Per-jurisdiction clause templates (jurisdiction_code, document_type, template_data)
- `GeneratedDocument` — AI-generated documents with status tracking (content, document_type, status)
- `ApprovalRequest` — Document approval requests (status, reviewer, notes)
- `ChatConversation` — Chat session metadata (title, employee_id)
- `ChatMessage` — Individual chat messages (role, content, sources)
- `ComplianceItem` — Compliance tracking items (type, status, expiry_date, risk_level)

### Enums
- `StepType` — 10 values: parse_data, detect_jurisdiction, employment_contract, nda, equity_agreement, offer_letter, welcome_email, plan_30_60_90, schedule_events, equipment_request
- `WorkflowStatus` — pending, running, completed, failed, paused, **awaiting_approval**
- `DocumentStatus` — draft, pending_review, approved, rejected, revision_requested
- `ApprovalStatus` — pending, approved, rejected, revision_requested
- `ComplianceStatus` — valid, expiring_soon, expired, pending

---

## API Endpoints

### Existing Routers
- `POST /api/auth/register` — User registration
- `POST /api/auth/login` — JWT login
- `GET/POST /api/employees` — Employee CRUD
- `POST /api/onboarding/{id}/start` — Start workflow (SSE streaming)
- `GET/POST /api/policies` — Policy management + PDF upload

### New Routers

#### Jurisdictions (`/api/jurisdictions`)
- `GET /` — List all jurisdictions
- `GET /{code}` — Get jurisdiction info
- `GET /{code}/templates` — Get templates for a jurisdiction

#### Documents (`/api/documents`)
- `GET /employee/{id}` — Get documents for an employee
- `GET /{id}` — Get document details
- `PUT /{id}` — Update document
- `GET /{id}/download` — Download document content

#### Approvals (`/api/approvals`)
- `GET /` — List all approval requests
- `GET /pending/count` — Get pending approval count
- `GET /{id}` — Get approval details
- `POST /{id}/approve` — Approve a document
- `POST /{id}/reject` — Reject a document
- `POST /{id}/revision` — Request revision
- `GET /employee/{id}` — Get approvals for an employee

#### Chat (`/api/chat`)
- `POST /conversations` — Create new conversation
- `GET /conversations` — List conversations
- `GET /conversations/{id}` — Get conversation details
- `GET /conversations/{id}/messages` — Get messages
- `POST /conversations/{id}/messages` — Send message (returns answer)
- `POST /conversations/{id}/stream` — Send message (SSE streaming)

#### Compliance (`/api/compliance`)
- `GET /` — List all compliance items
- `GET /summary` — Get compliance summary with rate
- `GET /alerts` — Get expiring/expired items
- `GET /expired` — Get expired items only
- `GET /predictions` — Get predictive alerts
- `GET /employee/{id}` — Get compliance items for employee
- `POST /` — Create compliance item

---

## API Testing

A simple HTML test page will be available at `backend/tests/test_page.html` for manual API testing without Postman.

Access it by:
1. Starting the backend server
2. Opening `http://localhost:8000/test` in browser
3. Use the forms to test each endpoint

---

## Development Commands

### Frontend
```bash
cd frontend
npm install
npm run dev          # Development server (port 3000)
npm run build        # Production build
npm run lint         # ESLint
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Backend (.env)
```env
DATABASE_URL=sqlite:///./data/onboarding.db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
VOYAGE_API_KEY=your-voyage-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

## Code Style Guidelines

### TypeScript/React
- Use functional components with hooks
- Prefer `interface` over `type` for object shapes
- Use absolute imports (`@/components/...`)
- shadcn/ui components for ALL UI elements

### Python
- Type hints on all functions
- Async functions where applicable
- Pydantic models for request/response validation
- Service layer pattern (routers → services → database)

---

## Current Development Phase

**Phase 1: Foundation** ✅ COMPLETE
- [x] Project setup with Next.js + FastAPI
- [x] shadcn/ui installation and configuration
- [x] Authentication pages (login, signup) + JWT
- [x] Basic layout and navigation
- [x] Employee management CRUD
- [x] RAG pipeline (ChromaDB + Voyage AI)
- [x] 6-step orchestrator pipeline with SSE streaming
- [x] Workflow visualizer with React Flow
- [x] Policy upload and management

**Phase 2: Feature Expansion** ✅ COMPLETE
- [x] Jurisdiction selector & multi-country support (US, UK, AE)
- [x] Expanded document generation (Employment Contract, NDA, Equity, Offer Letter)
- [x] Human approval workflow with approval gate in pipeline
- [x] Policy chatbot with RAG + conversation history
- [x] Compliance tracking & predictive alerts
- [x] Navigation updates (Approvals, Chat, Compliance pages)
- [x] 10-step pipeline with approval gate between documents and post-approval steps
- [x] Dashboard enhancements (compliance alerts, pending approvals)

**Status:** Phase 2 Complete — All features implemented

---

## Commands for Claude Code

When asked to work on this project:

1. **Check current state first** — Read existing files before modifying
2. **Use shadcn/ui** — Never create custom UI components from scratch
3. **Incremental changes** — Small, focused modifications
4. **Preserve manual changes** — Look for `// MANUAL:` comments
5. **Test after changes** — Suggest testing commands

---

## Questions to Ask Before Major Changes

1. "Should I preserve the existing structure or refactor?"
2. "Are there any manual changes I should be aware of?"
3. "Which shadcn/ui components should I use for this?"
4. "Should this be a client or server component?"
