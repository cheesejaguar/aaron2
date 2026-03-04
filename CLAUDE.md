# 🤖 CLAUDE.md — Aaron 2.0

> Instructions for Claude Code when working on this project.

## 📋 Project Overview

Aaron 2.0 is a single-user, locally-hosted health & nutrition app. The user is **Aaron** — there is no multi-tenant auth. A default user (`aaron@aaron2.local`) is auto-created on startup.

**North Star:** Help the user lose weight, lower cholesterol, and lower blood pressure through AI-powered grocery tracking, meal planning, and health metrics. 🎯

## 🏗️ Architecture

- **Monorepo** with `backend/` (Python) and `frontend/` (React)
- **Docker Compose** orchestrates: `app` (Nginx + FastAPI + frontend), `postgres`, `redis`, `celery`
- Single container serves both frontend (static via Nginx) and backend (proxied `/api/v1`)
- **No authentication** — `get_current_user` always returns the default user

## ⚡ Quick Commands

### 🐍 Backend
```bash
cd backend
ruff check .                    # Lint
ruff format --check .           # Format check
pytest -v --cov=app             # Run tests (179 tests)
alembic upgrade head            # Run migrations
```

### ⚛️ Frontend
```bash
cd frontend
npx tsc --noEmit                # Type check
npx eslint .                    # Lint
npx vitest run                  # Run tests (16 tests)
npm run build                   # Production build → dist/
```

### 🐳 Docker
```bash
docker compose up -d --build              # Full stack
docker compose up -d --build app          # Rebuild app only
docker compose logs -f app                # Tail app logs
docker compose exec postgres psql -U aaron2 aaron2  # DB shell
```

## 📐 Code Conventions

### 🐍 Backend (Python)
- **Framework:** FastAPI + SQLModel
- **Linter:** Ruff (replaces black, isort, flake8)
- **Import order:** stdlib → third-party → local (enforced by Ruff I001)
- **Models:** SQLModel classes in `backend/app/models/`
- **Routes:** `backend/app/api/v1/` — all endpoints use `Depends(get_current_user)`
- **Services:** Business logic in `backend/app/services/` (AI calls, nutrition calc)
- **Tasks:** Celery background tasks in `backend/app/tasks/`
- **Tests:** Pytest in `backend/tests/` using factory fixtures in `conftest.py`
- **Database:** PostgreSQL with Alembic migrations in `backend/alembic/`

### ⚛️ Frontend (TypeScript/React)
- **Framework:** React 18 + Vite + TypeScript strict mode
- **State:** TanStack Query for server state, Zustand for UI state
- **Components:** shadcn/ui (Radix primitives) in `frontend/src/components/ui/`
- **Styling:** Tailwind CSS v4
- **Forms:** React Hook Form + Zod validation schemas in `frontend/src/lib/validations.ts`
- **API layer:** Typed Axios clients in `frontend/src/api/`

### 🎨 Design System
- **Fonts:** DM Serif Display (headings), Outfit (body) — loaded via Google Fonts in `index.html`
- **Heading style:** `style={{ fontFamily: "'DM Serif Display', serif" }}`
- **Page containers:** `className="space-y-8 max-w-[1400px]"`
- **Cards:** `rounded-2xl border border-border/40` with gradient tint backgrounds
- **Micro-labels:** `text-[11px] font-semibold uppercase tracking-widest`
- **Form labels:** `text-xs font-semibold uppercase tracking-widest text-muted-foreground/60`
- **Buttons:** `rounded-xl h-10 px-4`
- **Inputs:** `rounded-xl border-border/40 bg-muted/20`
- **Animations:** `meal-card-enter` class with staggered `animationDelay` values
- **Secondary text:** `text-muted-foreground/50 font-light`
- **Dialogs:** `rounded-2xl` with serif titles

### 🤖 AI Integration
- All AI calls go through `backend/app/services/ai_service.py`
- Uses OpenRouter API with model routing per task type
- Responses cached in Redis (24h TTL)
- Cost tracking per request in the database

## ⚠️ Important Notes

- 🚫 **No auth system** — don't add login/register flows
- 🏠 **Single user** — `DEFAULT_USER_EMAIL = "aaron@aaron2.local"` in `backend/app/api/deps.py`
- 🐳 **Always rebuild after frontend changes:** `npm run build` then `docker compose up -d --build app`
- 📦 **Frontend is bundled into the Docker image** — Nginx serves `dist/` at `/`
- 🔄 **Migrations run on container startup** via supervisor before uvicorn starts
- ⏱️ **Default user creation** has retry logic (10 attempts, 2s delay) for migration race condition
