# COPILOT.md — GitHub Copilot Instructions

## Project: Zero-Touch Onboarding Orchestrator

AI-powered employee onboarding automation platform. Hackathon project focusing on workflow orchestration, RAG-based document generation, and real-time visualization.

---

## 📚 Documentation Links — REFERENCE THESE FOR ACCURATE CODE

Always consult official documentation to avoid deprecated patterns and outdated APIs.

### Frontend Docs

| Library | URL |
|---------|-----|
| Next.js (latest) | https://nextjs.org/docs |
| React 18 | https://react.dev/reference/react |
| shadcn/ui | https://ui.shadcn.com/docs |
| Tailwind CSS | https://tailwindcss.com/docs |
| React Flow (@xyflow/react) | https://reactflow.dev/docs |
| NextAuth.js v5 | https://authjs.dev/getting-started |
| Lucide Icons | https://lucide.dev/icons |
| React Dropzone | https://react-dropzone.js.org |
| Zod | https://zod.dev |
| TypeScript | https://www.typescriptlang.org/docs |

### Backend Docs

| Library | URL |
|---------|-----|
| FastAPI | https://fastapi.tiangolo.com |
| SQLAlchemy 2.0 | https://docs.sqlalchemy.org/en/20 |
| Pydantic V2 | https://docs.pydantic.dev/latest |
| ChromaDB | https://docs.trychroma.com |
| LangChain | https://python.langchain.com/docs |
| OpenAI Python | https://platform.openai.com/docs/api-reference |
| Anthropic Python | https://docs.anthropic.com/en/api |
| Voyage AI | https://docs.voyageai.com |
| PyMuPDF | https://pymupdf.readthedocs.io/en/latest |
| Pandas | https://pandas.pydata.org/docs |
| Python-Jose | https://python-jose.readthedocs.io/en/latest |
| Passlib | https://passlib.readthedocs.io/en/stable |

### Google APIs

| API | URL |
|-----|-----|
| Google Calendar API | https://developers.google.com/calendar/api/guides/overview |
| Google Auth | https://google-auth.readthedocs.io/en/latest |

### Deployment

| Platform | URL |
|----------|-----|
| Vercel | https://vercel.com/docs |
| Railway | https://docs.railway.app |

---

## ⚠️ Important: Manual Code Changes

The developer frequently makes manual code modifications. Copilot should:

- **DO NOT** assume file contents — check actual file state
- **PRESERVE** code blocks marked with `// MANUAL:` or `# MANUAL:`
- **ASK** before suggesting large refactors
- **RESPECT** existing patterns and structures in the codebase

---

## Tech Stack Summary

| Layer | Technology | Docs |
|-------|------------|------|
| Frontend | Next.js 15 (App Router), shadcn/ui, Tailwind CSS, React Flow | [Next.js](https://nextjs.org/docs), [shadcn](https://ui.shadcn.com/docs) |
| Backend | FastAPI, SQLAlchemy, SQLite, ChromaDB | [FastAPI](https://fastapi.tiangolo.com), [SQLAlchemy](https://docs.sqlalchemy.org/en/20) |
| Auth | NextAuth.js v5 (frontend), JWT + Google OAuth (backend) | [Auth.js](https://authjs.dev) |
| AI | OpenAI GPT-4 / Claude API, Voyage AI Embeddings | [OpenAI](https://platform.openai.com/docs), [Voyage AI](https://docs.voyageai.com) |
| Deployment | Vercel (frontend), Railway (backend) | [Vercel](https://vercel.com/docs), [Railway](https://docs.railway.app) |

---

## UI Component Library: shadcn/ui

**CRITICAL:** Use shadcn/ui for ALL user interface components. Do not create custom components when shadcn/ui provides an equivalent.

### Available Components (installed)
```
button, card, input, label, select, textarea,
dialog, alert-dialog, dropdown-menu,
table, tabs, toast, avatar, badge,
form, separator, skeleton, progress
```

### Import Pattern
```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
```

### Component Usage Examples
```tsx
// Buttons
<Button variant="default">Primary</Button>
<Button variant="outline">Secondary</Button>
<Button variant="destructive">Delete</Button>
<Button variant="ghost">Ghost</Button>

// Cards
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content here</CardContent>
</Card>

// Form inputs
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" placeholder="email@example.com" />
</div>
```

---

## Project Structure

```
zero-touch-onboarding/
├── frontend/                    # Next.js 14 App
│   ├── app/                     # App Router
│   │   ├── (auth)/              # Auth route group
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── employees/page.tsx
│   │   ├── onboarding/[id]/page.tsx
│   │   ├── policies/page.tsx
│   │   ├── settings/page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                  # shadcn/ui (DO NOT MODIFY)
│   │   ├── layout/              # Layout components
│   │   ├── onboarding/          # Feature components
│   │   └── shared/              # Shared components
│   ├── lib/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── utils.ts
│   ├── hooks/
│   ├── types/
│   └── styles/
│
├── backend/                     # FastAPI App
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── employees.py
│   │   │   ├── policies.py
│   │   │   ├── onboarding.py
│   │   │   └── calendar.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── orchestrator.py
│   │   │   ├── rag.py
│   │   │   ├── llm.py
│   │   │   ├── embeddings.py      # Voyage AI embedding provider
│   │   │   └── calendar.py
│   │   └── prompts/
│   ├── data/
│   ├── tests/
│   │   └── test_page.html       # HTML API testing page
│   └── requirements.txt
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

> **Note:** React Flow is now `@xyflow/react` in v12+. See [migration guide](https://reactflow.dev/learn/troubleshooting/migrate-to-v12).

---

## Backend Dependencies

```txt
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
```

---

## Code Patterns

### Frontend — Next.js App Router

**Page Component Pattern:**
```tsx
// app/dashboard/page.tsx
import { Metadata } from "next"

export const metadata: Metadata = {
  title: "Dashboard | Zero-Touch Onboarding",
}

export default function DashboardPage() {
  return (
    <div className="container mx-auto py-6">
      {/* Content */}
    </div>
  )
}
```

**Client Component Pattern:**
```tsx
// components/onboarding/WorkflowVisualizer.tsx
"use client"

import { useState, useEffect } from "react"
import { ReactFlow, Background, Controls } from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import { Card, CardContent } from "@/components/ui/card"

interface WorkflowVisualizerProps {
  employeeId: string
}

export function WorkflowVisualizer({ employeeId }: WorkflowVisualizerProps) {
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])
  
  // Component logic
  
  return (
    <Card>
      <CardContent className="h-[500px]">
        <ReactFlow nodes={nodes} edges={edges}>
          <Background />
          <Controls />
        </ReactFlow>
      </CardContent>
    </Card>
  )
}
```

> **Note:** Import from `@xyflow/react` not `reactflow`. See [React Flow docs](https://reactflow.dev/docs).

**API Client Pattern:**
```tsx
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL

export async function fetchEmployees() {
  const res = await fetch(`${API_URL}/api/employees`)
  if (!res.ok) throw new Error("Failed to fetch employees")
  return res.json()
}

export async function startOnboarding(employeeId: string) {
  const res = await fetch(`${API_URL}/api/onboarding/${employeeId}/start`, {
    method: "POST",
  })
  if (!res.ok) throw new Error("Failed to start onboarding")
  return res.json()
}
```

### Backend — FastAPI

**Router Pattern:**
```python
# app/routers/employees.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import EmployeeCreate, EmployeeResponse
from app.services import employee_service

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.get("/", response_model=list[EmployeeResponse])
async def get_employees(db: Session = Depends(get_db)):
    return employee_service.get_all(db)

@router.post("/", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_service.create(db, employee)
```

**Service Pattern:**
```python
# app/services/employee_service.py
from sqlalchemy.orm import Session
from app.models import Employee
from app.schemas import EmployeeCreate

def get_all(db: Session) -> list[Employee]:
    return db.query(Employee).all()

def create(db: Session, employee: EmployeeCreate) -> Employee:
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee
```

**Pydantic Schema Pattern:**
```python
# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    department: str
    start_date: date
    manager_email: Optional[EmailStr] = None
    buddy_email: Optional[EmailStr] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    status: str
    
    class Config:
        from_attributes = True
```

---

## Authentication

### Frontend (NextAuth.js v5 / Auth.js)

```tsx
// auth.ts (root level)
import NextAuth from "next-auth"
import Google from "next-auth/providers/google"
import Credentials from "next-auth/providers/credentials"

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // Validate against backend
      },
    }),
  ],
})

// app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/auth"
export const { GET, POST } = handlers
```

> **Note:** NextAuth.js v5 uses a different API. See [Auth.js docs](https://authjs.dev/getting-started).

### Backend (JWT)

```python
# app/services/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
```

---

## API Testing Page

Backend includes an HTML test page at `backend/tests/test_page.html` for manual API testing without Postman.

Features:
- Forms for each endpoint
- JSON response display
- Authentication token management
- File upload testing

---

## Development Commands

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### Backend (.env)
```
DATABASE_URL=sqlite:///./data/onboarding.db
SECRET_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
VOYAGE_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

---

## Key Features

1. **Visual Workflow Graph** — React Flow with animated status transitions
2. **RAG for Policies** — ChromaDB + Voyage AI embeddings for document retrieval
3. **Agent Thinking Panel** — SSE streaming of AI reasoning
4. **File Upload** — CSV for employees, PDF for policies
5. **Google Calendar** — OAuth + event scheduling

---

## Embedding Provider: Voyage AI

We use **Voyage AI** as the primary embedding provider. Free tier includes 50M tokens (no credit card required).

**Code Pattern — Voyage AI with ChromaDB:**
```python
# app/services/embeddings.py
import voyageai
import os
from typing import List

class VoyageEmbeddingFunction:
    """ChromaDB-compatible embedding function using Voyage AI."""
    def __init__(self):
        self.client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.model = "voyage-2"
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        result = self.client.embed(texts=input, model=self.model)
        return result.embeddings
```

**Using with ChromaDB:**
```python
from app.services.embeddings import VoyageEmbeddingFunction

ef = VoyageEmbeddingFunction()
collection = chroma_client.get_or_create_collection(
    name="policy_documents",
    embedding_function=ef,
)
```

**LangChain Integration:**
```python
from langchain_voyageai import VoyageAIEmbeddings

embeddings = VoyageAIEmbeddings(
    voyage_api_key=os.getenv("VOYAGE_API_KEY"),
    model="voyage-2"
)
```

---

## Copilot Suggestions Guidelines

### DO:
- Use shadcn/ui components for all UI
- Follow existing file patterns
- Add TypeScript types
- Use async/await for API calls
- Include error handling

### DON'T:
- Create custom UI components when shadcn/ui has them
- Ignore existing code structure
- Remove `// MANUAL:` marked code
- Use class components in React
- Skip type annotations

---

## Current Phase: Frontend Foundation

Backend status: **✅ COMPLETE** (all endpoints, services, AI agent, RAG, embeddings)

Building order:
1. ✓ Project setup
2. ✓ Backend — FastAPI, SQLAlchemy, JWT auth, all endpoints
3. ✓ AI Agent — LLM integration, prompt templates, orchestrator pipeline
4. ✓ RAG — ChromaDB + Voyage AI embeddings, PDF processing
5. ✓ Mock fallbacks — LLM mock, calendar mock, embedding fallback
6. → Authentication UI (Google + Email/Password)
7. → Basic layout and navigation
8. → Employee management pages
9. → Workflow visualizer
10. → Backend integration
