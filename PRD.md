# Aaron 2.0 — Claude Code Project Prompt

> Paste this entire document into Claude Code's **Plan mode** first, review the plan, then execute.

---

## Project Vision

Build **Aaron 2.0** — a locally-hosted, AI-powered web application for grocery tracking, meal planning, and health metrics. The North Star of this app is to use AI to help the user **lose weight, lower cholesterol, and lower blood pressure**. Every feature should be oriented around this goal.

---

## Tech Stack

### Frontend
- **React 18** with **TypeScript** (strict mode)
- **Vite** for bundling and dev server
- **Tailwind CSS** + **shadcn/ui** for components
- **React Query (TanStack Query v5)** for server state
- **Zustand** for client state
- **Recharts** for data visualization and dashboards
- **React Hook Form** + **Zod** for form validation
- **React Router v6** for navigation

### Backend
- **Python 3.12** with **FastAPI**
- **SQLModel** (SQLAlchemy + Pydantic, unified models)
- **PostgreSQL 16** as the primary database
- **Alembic** for database migrations
- **Celery** + **Redis** for background task queue (receipt parsing, auto-replenishment)
- **Uvicorn** ASGI server

### AI Integration
- **OpenRouter API** (`https://openrouter.ai/api/v1`) using the OpenAI-compatible SDK
- Model strategy (see AI Model Strategy section below)

### Infrastructure
- **Single Docker container** using Docker multi-stage build (dev + prod targets)
- **Docker Compose** orchestrating: app, postgres, redis
- **Nginx** as reverse proxy serving frontend build + proxying `/api` to FastAPI
- **GitHub Actions** CI/CD pipeline

### Testing
- **Pytest** + **pytest-asyncio** for backend unit and integration tests
- **Factory Boy** for test fixtures
- **HTTPX** for async API client testing
- **Vitest** for frontend unit tests
- **React Testing Library** for component tests
- **Playwright** for end-to-end tests
- **Coverage.py** targeting ≥80% backend coverage

---

## AI Model Strategy (OpenRouter)

Use `https://openrouter.ai/api/v1` with the standard OpenAI SDK (`openai` Python package with `base_url` override). All AI calls must include `X-Title: Aaron 2.0` and `HTTP-Referer: http://localhost` headers.

Implement a central `AIService` class that selects models based on task complexity:

| Task | Model | Rationale |
|------|-------|-----------|
| Email receipt parsing (complex, multimodal reasoning) | `deepseek/deepseek-v3-2` | GPT-5 class at fraction of cost |
| Recipe generation and meal planning | `deepseek/deepseek-v3-2` | Complex nutritional reasoning |
| Health coaching insights / dashboard analysis | `anthropic/claude-sonnet-4-6` | Nuanced health guidance |
| Simple classification (is this food healthy?) | `google/gemini-3-flash` | Fast, cheap, accurate |
| Auto-categorizing grocery items | `google/gemini-3-flash` | Lightweight classification |
| Generating shopping list descriptions | `meta-llama/llama-3.3-70b-instruct` | Free tier, adequate for simple generation |
| Macro estimation from food name | `google/gemini-3-flash` | Real-time estimation, low latency needed |

Implement retry logic with exponential backoff, response caching (Redis) with TTL=24h for identical prompts, and cost tracking logged to the database.

---

## Core Features

### 1. Email Receipt Parser
- Upload or paste raw email text from Amazon Fresh / Whole Foods / any grocery receipt
- AI (DeepSeek V3.2) extracts: item name, quantity, unit price, category, estimated nutrition per unit
- Parsed items populate the **Pantry** (current stock)
- Track purchase history for trend analysis
- Support for Gmail OAuth integration to pull receipts automatically (optional flow)

### 2. Pantry & Inventory Tracking
- Current pantry state: item name, quantity, unit, category, expiry date estimate, nutrition data
- AI auto-categorizes items (produce, dairy, protein, pantry staple, snack, beverage)
- "Consume" UI: log consuming a portion of any pantry item — updates stock and logs to daily nutrition
- Low stock alerts when item falls below configurable threshold
- Expiry warnings 3 days before estimated expiry

### 3. Meal Planning
- Weekly meal planner (7-day grid, 3 meals + snacks per day)
- AI meal recommendation engine (DeepSeek V3.2): given current pantry, health goals (weight loss, lower BP, lower cholesterol), and dietary preferences, suggest meals for the week
- Recommendations must explicitly prioritize: high fiber, low sodium, DASH-diet principles, potassium-rich foods, omega-3s
- Each recommended meal shows: full nutrition breakdown, ingredients required, which ingredients are already in pantry vs. need to be purchased
- Drag-and-drop meal rescheduling

### 4. Recipe Library
- Browse, search, and save recipes
- Each recipe: ingredients list, steps, nutrition per serving, health tags (heart-healthy, low-sodium, high-potassium, etc.)
- AI recipe generation: user describes what they want ("high-protein pasta that helps lower BP") and AI generates a complete recipe
- **"Add Recipe to Shopping List"**: one-click adds all missing ingredients (not in pantry) to the active shopping list
- Import recipes from URL (scrape + AI parse)

### 5. Shopping List Manager
- Create and manage multiple shopping lists
- Auto-replenishment engine (Celery background job): analyzes pantry consumption rate, predicts when items will run low, automatically adds to shopping list
- AI prioritizes shopping list by health impact — flags which items are most critical for BP/cholesterol/weight goals
- **Amazon Cart Integration**: Generate a pre-filled Amazon Fresh cart URL using Amazon's affiliate deep-link format (`https://www.amazon.com/afx/ingredients/add?...`). This creates a shareable cart link the user clicks to auto-populate their Amazon Fresh cart. Document this clearly as a "cart builder" (not direct API ordering, which requires Amazon SP-API seller credentials).
- Export shopping list as PDF or share link
- Check off items while shopping (mobile-friendly UI)

### 6. Nutrition & Macro Tracker
- Daily food log: each consumed item or meal logs macros (calories, protein, fat, carbs, fiber, sodium, potassium, cholesterol)
- Daily targets configurable by user (defaults set for weight loss + BP reduction: ~1800 cal, <1500mg sodium, >4700mg potassium, >25g fiber)
- Progress rings / bar charts for daily macro targets
- AI daily summary: "You're 800mg over sodium today, mainly from the deli turkey. Here's how to balance dinner."

### 7. Health Metrics Dashboard
- Blood pressure log: manual entry of systolic/diastolic/pulse, with timestamp
- Weight log
- Cholesterol log (manual lab result entry)
- Trend charts over time (7-day, 30-day, 90-day views) using Recharts
- AI health coach insights panel (Claude Sonnet 4.6): weekly summary analyzing trends, connecting diet patterns to health metrics, making specific actionable recommendations
- Color-coded status indicators: green/yellow/red for BP ranges (normal <120/80, elevated 120-129/<80, Stage 1 130-139/80-89, Stage 2 ≥140/90)
- Export health data as CSV or PDF report

### 8. AI Health Coach Chat
- Persistent chat interface with an AI health coach (Claude Sonnet 4.6)
- Coach has full context of: current pantry, recent meals, macro trends, BP/weight/cholesterol history
- Can answer questions like "what should I eat tonight to help my BP?", "am I getting enough potassium this week?", "explain why my cholesterol might be high"
- Conversation history persisted in database
- Coach proactively surfaces alerts (e.g., "Your sodium has been high 5 days in a row")

---

## Database Schema

Design the following SQLModel tables:

```
User (id, email, name, created_at, health_goals_json)
PantryItem (id, user_id, name, category, quantity, unit, nutrition_json, purchase_date, estimated_expiry, low_stock_threshold)
PurchaseReceipt (id, user_id, raw_text, parsed_at, source, items_json)
Recipe (id, user_id, title, description, ingredients_json, steps_json, nutrition_per_serving_json, health_tags, source_url, is_ai_generated)
MealPlan (id, user_id, week_start_date)
MealPlanEntry (id, meal_plan_id, day_of_week, meal_type, recipe_id, custom_meal_json)
ShoppingList (id, user_id, name, created_at, status)
ShoppingListItem (id, shopping_list_id, pantry_item_ref, name, quantity, unit, category, is_checked, is_ai_suggested, health_priority_score)
FoodLog (id, user_id, logged_at, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg, potassium_mg, cholesterol_mg)
BloodPressureLog (id, user_id, logged_at, systolic, diastolic, pulse, notes)
WeightLog (id, user_id, logged_at, weight_lbs, notes)
CholesterolLog (id, user_id, logged_at, total_mg_dl, ldl, hdl, triglycerides, notes)
AIConversation (id, user_id, created_at, messages_json)
AIUsageLog (id, model, prompt_tokens, completion_tokens, cost_usd, task_type, created_at)
```

---

## API Design

RESTful API under `/api/v1/`. All endpoints return JSON. Use FastAPI's dependency injection for auth and DB sessions.

Key route groups:
- `POST /api/v1/receipts/parse` — AI receipt parsing
- `GET/POST/DELETE /api/v1/pantry` — pantry CRUD
- `POST /api/v1/pantry/{id}/consume` — log consumption
- `GET/POST /api/v1/recipes` — recipe CRUD
- `POST /api/v1/recipes/generate` — AI recipe generation
- `POST /api/v1/recipes/import-url` — scrape + parse recipe
- `GET/POST /api/v1/meal-plans` — weekly planner
- `POST /api/v1/meal-plans/suggest` — AI meal suggestions
- `GET/POST /api/v1/shopping-lists` — list CRUD
- `POST /api/v1/shopping-lists/{id}/replenish` — trigger AI replenishment
- `GET /api/v1/shopping-lists/{id}/amazon-cart-url` — generate Amazon cart URL
- `GET/POST /api/v1/food-log` — daily food log
- `GET /api/v1/nutrition/daily-summary` — macro totals for a date
- `GET/POST /api/v1/health/blood-pressure` — BP log
- `GET/POST /api/v1/health/weight` — weight log
- `GET/POST /api/v1/health/cholesterol` — cholesterol log
- `GET /api/v1/health/dashboard` — aggregated dashboard data
- `POST /api/v1/coach/chat` — AI health coach message
- `GET /api/v1/coach/insights` — weekly AI health insights

---

## UI/UX Design

Use a clean, modern dark-mode-first design with Tailwind + shadcn/ui. Color palette:
- Background: `#0f172a` (slate-900)
- Card: `#1e293b` (slate-800)
- Accent: `#22c55e` (green-500) — represents health/progress
- Warning: `#f59e0b` (amber-500)
- Danger: `#ef4444` (red-500)
- Text: `#f1f5f9` (slate-100)

### Layout
- Collapsible sidebar navigation on left
- Main content area
- Persistent AI coach chat panel (right side, toggleable)

### Pages / Views
1. **Dashboard** — health metrics overview, today's nutrition progress, pantry alerts, recent AI insights
2. **Pantry** — grid/list of current items, search/filter by category, add item manually or via receipt
3. **Meal Planner** — weekly calendar grid with drag-and-drop meals
4. **Recipes** — searchable library + AI recipe generator
5. **Shopping List** — active list with check-off UI + Amazon cart button
6. **Food Log** — today's log with quick-add, macro rings
7. **Health Metrics** — BP/weight/cholesterol logs + trend charts
8. **AI Coach** — full-screen chat interface
9. **Settings** — health goals, dietary preferences, notification thresholds

---

## Docker & Infrastructure

### Docker Compose Services
```yaml
services:
  app:       # FastAPI + Nginx (multi-stage build: frontend built in Node stage, served by Nginx)
  postgres:  # PostgreSQL 16 with persistent volume
  redis:     # Redis 7 for Celery broker and AI response cache
  celery:    # Celery worker (same image as app, different CMD)
```

### Multi-Stage Dockerfile
- **Stage 1 (frontend-builder)**: Node 20 Alpine, builds React/Vite app to `/dist`
- **Stage 2 (backend)**: Python 3.12 slim, installs dependencies
- **Stage 3 (production)**: Nginx + Python, copies frontend build + backend, runs supervisord to manage both Nginx and Uvicorn

### Environment Variables
All secrets via `.env` file (never committed):
```
OPENROUTER_API_KEY=
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379/0
SECRET_KEY=
```

---

## Testing Strategy

### Backend Tests (`/backend/tests/`)
- `test_api/` — integration tests for every API endpoint using HTTPX async client + test database
- `test_services/` — unit tests for AI service, receipt parser, replenishment engine
- `test_models/` — SQLModel validation tests
- Use `pytest-cov` with `--cov-fail-under=80`
- Mock all OpenRouter API calls in tests using `respx` (HTTPX mocker)
- Use `factory_boy` for realistic test data factories

### Frontend Tests (`/frontend/src/__tests__/`)
- Vitest + React Testing Library for component tests
- Test all form validations, state transitions, error states
- Mock API calls with MSW (Mock Service Worker)

### E2E Tests (`/e2e/`)
- Playwright tests for critical user flows:
  1. Upload receipt → items appear in pantry
  2. Generate AI meal plan → meals populate weekly planner
  3. Add recipe → missing ingredients added to shopping list
  4. Log blood pressure → dashboard chart updates
  5. Chat with AI coach → receives contextual response

### CI/CD (`.github/workflows/`)

**`ci.yml`** — runs on every PR:
```
jobs:
  backend-test:   pytest with coverage report
  frontend-test:  vitest
  e2e:            playwright (headless)
  lint:           ruff (Python) + eslint + prettier
  type-check:     mypy (Python strict) + tsc --noEmit
  docker-build:   build Docker image to verify it compiles
```

**`cd.yml`** — runs on merge to `main`:
```
jobs:
  deploy:   SSH to Linux server, pull latest, docker compose up -d --build
```

---

## Project Structure

```
aaron-2/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── routes/          # One file per route group
│   │   │       └── deps.py          # FastAPI dependencies (DB, auth)
│   │   ├── models/                  # SQLModel table definitions
│   │   ├── services/
│   │   │   ├── ai_service.py        # Central OpenRouter client
│   │   │   ├── receipt_parser.py
│   │   │   ├── meal_planner.py
│   │   │   ├── replenishment.py
│   │   │   ├── nutrition.py
│   │   │   └── health_coach.py
│   │   ├── tasks/                   # Celery tasks
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic settings
│   │   │   └── database.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── dashboard/
│   │   │   ├── pantry/
│   │   │   ├── recipes/
│   │   │   ├── shopping/
│   │   │   ├── health/
│   │   │   └── coach/
│   │   ├── pages/
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── stores/                  # Zustand stores
│   │   ├── api/                     # TanStack Query + axios API layer
│   │   ├── types/                   # TypeScript interfaces
│   │   └── __tests__/
│   ├── e2e/                         # Playwright tests
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
└── README.md
```

---

## Implementation Priorities (Build in this order)

1. **Foundation**: Docker Compose, FastAPI skeleton, PostgreSQL + Alembic migrations, React + Vite scaffold, Nginx config
2. **Core Models & CRUD**: All SQLModel tables, basic REST endpoints, React pages with placeholder UI
3. **AI Service Layer**: `AIService` class, OpenRouter integration, model routing, caching
4. **Receipt Parser**: Email upload UI + AI parsing pipeline + pantry population
5. **Pantry Management**: Full CRUD UI, consumption logging, low-stock alerts
6. **Food Log & Nutrition**: Daily logging, macro calculations, target tracking, progress UI
7. **Health Metrics**: BP/weight/cholesterol logging, Recharts dashboards
8. **Meal Planning**: Weekly planner UI, AI meal suggestion engine
9. **Recipe System**: Library, AI generation, URL import, shopping list integration
10. **Shopping List & Amazon Cart**: List manager, auto-replenishment, cart URL builder
11. **AI Health Coach**: Chat interface, context injection, proactive insights
12. **Testing**: Full test suite, CI/CD pipeline
13. **Polish**: Dark mode, mobile responsive, loading states, error boundaries, empty states

---

## Special Implementation Notes

### OpenRouter API Client
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "Aaron 2.0",
    }
)
```

### Amazon Cart URL Builder
Amazon Fresh supports ingredient deep-links. Build URLs in this format:
`https://www.amazon.com/afx/ingredients/add?ingredient[0][name]=<item>&ingredient[0][quantity]=<qty>&...`
This opens Amazon Fresh with items pre-searched. Document this clearly to user as "Open in Amazon Fresh" — it is not direct ordering, it opens a pre-filled search cart. Generate these server-side and return as a redirect URL.

### DASH Diet AI Prompt Engineering
All AI prompts related to meal planning and recipe generation must include this system context:
```
The user has Stage 2 hypertension (BP ~150/100), high cholesterol, and is pursuing weight loss.
Prioritize the DASH diet: high potassium (>4700mg/day), magnesium, fiber (>25g/day), low sodium (<1500mg/day),
lean protein, omega-3 fatty acids. Avoid high-sodium processed foods, saturated fats, added sugars.
Favor: leafy greens, berries, whole grains, legumes, fish, avocado, nuts, seeds, low-fat dairy.
Always explain the health benefit of each recommendation in terms the user can understand.
```

### Blood Pressure Status Logic
```python
def bp_status(systolic: int, diastolic: int) -> str:
    if systolic < 120 and diastolic < 80: return "normal"
    if systolic < 130 and diastolic < 80: return "elevated"
    if systolic < 140 or diastolic < 90: return "stage1"
    return "stage2"
```

### Celery Auto-Replenishment Task
Schedule with Celery Beat to run nightly at 9pm:
- Query all pantry items for the user
- Calculate consumption rate (purchases vs. food log entries over past 14 days)
- Predict days until depletion for each item
- Items predicted to deplete within 5 days → add to active shopping list with `is_ai_suggested=True`
- Notify via in-app notification

---

## Quality Standards

- All Python code must pass `ruff` linter and `mypy` strict type checking
- All TypeScript must pass `tsc --noEmit` with no errors
- All API endpoints must have OpenAPI docs (FastAPI auto-generates, but write clear docstrings)
- All database queries must use parameterized queries (no raw SQL string interpolation)
- Sensitive config (API keys, DB credentials) only via environment variables, never hardcoded
- All AI responses must be validated and have fallbacks (never crash the app on AI failure)
- Rate limiting on AI endpoints: max 10 requests/minute per user
- All health data must be treated as sensitive — implement basic auth (JWT) from day one

---

## README Requirements

The `README.md` must include:
- Project overview and North Star mission
- Prerequisites (Docker, Docker Compose)
- One-command setup: `docker compose up --build`
- Environment variable documentation
- How to run tests
- How to access the app (default: `http://localhost:3000`)
- OpenRouter API key setup instructions
- Architecture diagram (ASCII or Mermaid)
- Feature list with screenshots placeholder

---

*End of Aaron 2.0 Project Specification*