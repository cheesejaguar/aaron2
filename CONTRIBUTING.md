# 🤝 Contributing to Aaron 2.0

Thanks for your interest in contributing! Here's how to get started. 🚀

## 🛠️ Development Setup

### Prerequisites

- 🐳 Docker & Docker Compose
- 🐍 Python 3.12+
- 📦 Node.js 18+ & npm
- 🔑 OpenRouter API key

### 1️⃣ Fork & clone

```bash
git clone https://github.com/your-username/aaron2.git
cd aaron2
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY
```

### 2️⃣ Start the stack

```bash
docker compose up -d --build
```

The app will be running at `http://localhost:3000`. 🎉

### 3️⃣ Local development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev    # Vite dev server on :5173
```

## 📋 Making Changes

### 🌿 Branch naming

Use descriptive branch names:
- `feat/add-meal-export` — ✨ New features
- `fix/bp-chart-crash` — 🐛 Bug fixes
- `refactor/simplify-ai-service` — ♻️ Refactoring
- `docs/update-readme` — 📝 Documentation

### ✅ Before submitting

Run the full check suite:

```bash
# 🐍 Backend
cd backend
ruff check .                # Lint
ruff format --check .       # Format
pytest -v --cov=app         # Tests

# ⚛️ Frontend
cd frontend
npx tsc --noEmit            # Type check
npx eslint .                # Lint
npx vitest run              # Tests
npm run build               # Build succeeds
```

All checks must pass. ✅

### 💬 Commit messages

Write clear, concise commit messages:

```
feat: add serving size adjuster to recipe modal
fix: prevent crash when cholesterol data is empty
refactor: extract nutrition bar into reusable component
```

Use [conventional commits](https://www.conventionalcommits.org/) format. 📝

## 🎨 Design Guidelines

This project has a specific design language — please follow it! See `CLAUDE.md` for the full design system reference.

Key rules:
- 🔤 Use **DM Serif Display** for headings, **Outfit** for body text
- 🎯 Use `rounded-2xl border-border/40` for cards with gradient tint backgrounds
- 🏷️ Use `text-[11px] font-semibold uppercase tracking-widest` for micro-labels
- ✨ Use `meal-card-enter` CSS class for entrance animations
- 📐 Use `max-w-[1400px]` for page containers

## 🧪 Testing

- 🐍 **Backend:** Pytest with async fixtures. Tests in `backend/tests/`. Aim for ≥80% coverage.
- ⚛️ **Frontend:** Vitest + React Testing Library. Tests co-located with components.
- 🔌 **API tests:** Use the `client` and `test_user` fixtures from `conftest.py`.

## 🐛 Reporting Issues

When filing a bug report, please include:
1. 📝 Steps to reproduce
2. 🎯 Expected behavior
3. 💥 Actual behavior
4. 🖥️ Environment (OS, Docker version, browser)

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE.md). ⚖️
