# CyberShield

CyberShield is an educational cybersecurity platform for examining URL patterns, learning safer online habits, and keeping a private record of personal checks. It is designed as a portfolio-ready full-stack project using React, TypeScript, Vite, Tailwind CSS, FastAPI, SQLAlchemy, PostgreSQL, and SQLite for local development.

> **Assessment limitation:** URL results are automated preliminary assessments, not confirmed threat intelligence, a guarantee of safety, or a professional security audit. CyberShield never opens, crawls, or fetches submitted URLs.

## Features

- **URL pattern analysis:** Normalizes HTTP(S) URLs and explains rule-based indicators for insecure HTTP, IP-address hosts, long subdomain chains, account-related terms, misleading brand patterns, encoded separators, internationalized/punycode names, and unusual ports.
- **Transparent scoring:** Each finding includes its named rule and point value. Scores range from 0 to 100 and map to Low, Medium, High, or Critical.
- **Private accounts and history:** Argon2id password hashing, signed HttpOnly session cookies, account-scoped queries, and account deletion with owned data cleanup.
- **Dashboard and history:** Statistics, recent analyses, 14-day activity, category breakdowns, search, and category filters are calculated from stored user data. A new account starts with empty real-data statistics.
- **PDF reports:** Downloadable reports include the redacted address, timestamp, score, findings, explanations, recommendations, and an explicit preliminary-assessment disclaimer.
- **Learning center:** Six original modules—phishing, social engineering, password security, ransomware, malware, and safe browsing—with quizzes, answer explanations, best scores, and completion progress.
- **Privacy-minded URL handling:** Common secret query values and URL fragments are removed before storage; URLs are never made clickable by the application.
- **API documentation:** FastAPI's interactive documentation is available at `/api/docs` when the API service is running.

## Technology and architecture

- React + TypeScript + Vite; Tailwind CSS; Wouter; TanStack Query; Recharts; Lucide icons.
- Python 3.11+ + FastAPI + SQLAlchemy 2 + Alembic.
- PostgreSQL by default when `DATABASE_URL` is configured; SQLite file fallback for local development.
- Vitest and Testing Library for frontend component tests; pytest and FastAPI TestClient for backend tests.
- API routes are defined in `lib/api-spec/openapi.yaml`. Typed React Query hooks are generated with Orval.

See [architecture and data model](docs/architecture.md), [risk scoring](docs/risk-scoring.md), [API endpoint reference](docs/api-reference.md), and [implementation phases](docs/implementation-plan.md).

## Project structure

```text
artifacts/
  api-server/
    cybershield_api/
      main.py                 FastAPI app, security middleware, and app configuration
      database.py             PostgreSQL / SQLite SQLAlchemy setup
      models.py               Account, analysis, and lesson-progress models
      risk.py                 URL normalization and deterministic scoring rules
      security.py             Argon2id hashing and request rate limits
      learning.py             Original curriculum and quiz answer keys
      routes/                 Auth, analyses/reports, learning, and settings routes
    migrations/               Alembic migrations
    tests/                    pytest unit and API authorization tests
    pyproject.toml             Python dependencies and pytest configuration
    alembic.ini                Migration configuration
    .env.example               Safe environment-variable placeholders
  cybershield/
    src/                       React application, routes, and components
    .env.example               Optional local API origin
    vite.config.ts
lib/
  api-spec/openapi.yaml        API contract source of truth
  api-client-react/            Generated React Query client and shared fetcher
docs/
  architecture.md
  api-reference.md
  risk-scoring.md
  implementation-plan.md
```

## Prerequisites

- Node.js 24 (to match the workspace), Corepack/pnpm 10.
- Python 3.11 or newer and [`uv`](https://docs.astral.sh/uv/).
- PostgreSQL for a shared/durable database. SQLite is used automatically if `DATABASE_URL` is unset.

## Local setup

### Install workspace and Python packages

From the repository root:

```sh
corepack enable
pnpm install
uv sync --project artifacts/api-server
```

Copy `artifacts/api-server/.env.example` to `artifacts/api-server/.env` and replace the local session placeholder with a random value. Keep `.env` out of Git. For local SQLite, leave `DATABASE_URL` unset; the app creates `artifacts/api-server/cybershield.db` after applying migrations.

PowerShell can generate a session secret for the current terminal:

```powershell
$env:SESSION_SECRET = python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:ENVIRONMENT = "development"
$env:COOKIE_SECURE = "false"
```

If you prefer PostgreSQL, set `DATABASE_URL` to a local development database URL before running migrations. Never use production credentials for local development.

### Create or update the database schema

From the repository root:

```sh
uv run --directory artifacts/api-server alembic upgrade head
```

The initial migration creates `users`, `analyses`, and `learning_progress`. Migrations are explicit; the API does not run schema changes automatically at startup.

### Start the API

In one terminal, from the repository root:

```sh
pnpm --filter @workspace/api-server run dev
```

The API service listens on port `8080` and is mounted at `/api` in the Replit preview. Check `/api/healthz` and `/api/docs`.

### Start the web app

In a second terminal, use the Replit workflow named **CyberShield: web**. The frontend expects the shared `/api` route and needs no separate API origin in Replit.

For direct Windows/local development without the Replit proxy, run the API on port 5000 and the frontend on 5173. In PowerShell:

**API terminal**

```powershell
cd artifacts/api-server
$env:PORT = "5000"
$env:SESSION_SECRET = "replace-with-a-random-secret"
$env:ENVIRONMENT = "development"
$env:COOKIE_SECURE = "false"
uv sync
uv run alembic upgrade head
uv run python -m cybershield_api
```

**Frontend terminal**

```powershell
$env:PORT = "5173"
$env:BASE_PATH = "/"
$env:VITE_API_BASE_URL = "http://127.0.0.1:5000"
pnpm --filter @workspace/cybershield run dev
```

Open `http://127.0.0.1:5173`. The API allows the local Vite origins by default. Set `DATABASE_URL` in both terminal environments only if using PostgreSQL; otherwise SQLite is used. Do not set the backend secret in the browser environment.

The backend's `python -m cybershield_api` launcher reads `artifacts/api-server/.env` if it exists; process environment variables take precedence. For a direct Uvicorn launch, use `uv run uvicorn cybershield_api.main:app --env-file .env --host 127.0.0.1 --port 5000` from `artifacts/api-server`.

## Run checks

From the repository root:

```sh
pnpm --filter @workspace/api-server run test
pnpm --filter @workspace/cybershield run test
pnpm --filter @workspace/cybershield run typecheck
pnpm run typecheck
```

Backend tests cover URL parsing/scoring, input limits, password hashing, account sessions, private history authorization, report access, learning-score persistence, and deletion. Frontend tests exercise accessible component behavior. Test outcomes are not implied by this documentation; run the commands in the current checkout.

## Database and privacy

- PostgreSQL is selected through `DATABASE_URL`; without it the backend uses a local SQLite file.
- Passwords are stored only as Argon2id hashes. Session cookies are signed, HttpOnly, SameSite=Lax, and can be marked Secure with `COOKIE_SECURE=true`.
- The API uses parameterized SQL through SQLAlchemy and scopes analysis/report queries by the authenticated user ID.
- Request bodies are limited to 16 KiB. Login and registration have per-process IP-based limits; URL analysis has a per-account limit.
- Common sensitive query parameters (such as `token`, `password`, `key`, and `session`) and URL fragments are redacted before saving an analysis.
- Account deletion removes the user's account, analyses, and lesson progress.
- There is no sample account, demo scan history, external reputation lookup, or live AI/threat-intelligence feed. The current URL engine is explainable, deterministic heuristics.

## Deployment

### Replit

The project is configured with a web artifact at `/` and a FastAPI service at `/api`. Set `SESSION_SECRET` using Replit Secrets; use the managed PostgreSQL `DATABASE_URL`. Apply migrations to the target database with `uv run --directory artifacts/api-server alembic upgrade head` before serving a new version. Production service settings enable secure cookies. Publish only after reviewing the target database and environment.

### Vercel frontend + Render Python API

1. Deploy `artifacts/api-server` as a Python web service on Render. Build command: `uv sync --project artifacts/api-server --no-dev`. Start command: `uv run --directory artifacts/api-server uvicorn cybershield_api.main:app --host 0.0.0.0 --port $PORT`.
2. Add a Render PostgreSQL database, set `DATABASE_URL`, set a generated `SESSION_SECRET`, and set `ENVIRONMENT=production` and `COOKIE_SECURE=true`. Apply Alembic migrations before directing users to the app.
3. Deploy the Vite frontend from the repository root with the workspace dependencies available. Build command: `pnpm install --frozen-lockfile && pnpm --filter @workspace/cybershield run build`; output directory: `artifacts/cybershield/dist/public`.
4. Configure the frontend host to proxy `/api/:path*` to the Render service under the same public origin (for example, a Vercel rewrite). A same-origin rewrite lets the browser use the HttpOnly session cookie without exposing it to JavaScript.
5. Set `CORS_ORIGINS` on the API to the exact frontend origin if the hosting proxy forwards the browser `Origin` header. Keep the API and frontend on the same site; third-party cookie policies can block a direct cross-site deployment.

Do not put `SESSION_SECRET` or `DATABASE_URL` in any `VITE_*` variable. See the provider's current docs for account-specific setup and environment configuration.

## GitHub publishing checklist

- [ ] Review all tracked files; ensure `.env`, local database files, `.venv`, `.pythonlibs`, and secrets are excluded.
- [ ] Rotate any credential that was ever committed; removing it from the latest commit is not sufficient.
- [ ] Run the backend tests, frontend tests, and type checks.
- [ ] Review the README, architecture, risk-scoring rules, API reference, and screenshots.
- [ ] Do not include real user URLs, account data, production exports, or database dumps in screenshots or commits.
- [ ] Add an open-source license only if you are ready to choose one.
- [ ] Use a repository description that calls the URL results preliminary and rule-based.

## Screenshots worth capturing

1. Landing page and its plain-language disclaimer.
2. Empty dashboard for a fresh account.
3. An analysis showing both the final score and the individual weighted findings.
4. A saved analysis and its downloadable PDF report.
5. A learning module and a completed quiz with explanations.
6. Settings/privacy information and the account-deletion confirmation.

Use only demonstration URLs you control or reserved documentation addresses. Do not screenshot private URLs, passwords, tokens, or real account details.

## Resume bullets

- Built **CyberShield**, a full-stack cybersecurity education platform using React, TypeScript, FastAPI, SQLAlchemy, and PostgreSQL/SQLite, with private accounts, scan history, dashboards, and downloadable PDF reports.
- Designed an explainable URL risk-scoring engine that normalizes submitted HTTP(S) URLs locally, detects eight suspicious pattern classes, redacts common credential-bearing URL fields, and never makes outbound requests to user-submitted destinations.
- Implemented account-scoped API authorization, Argon2id password hashing, signed HttpOnly sessions, request-size limits, rate limiting, and Alembic database migrations.
- Authored six cybersecurity lessons with multiple-choice quizzes, explanations, persisted scores, and completion tracking; added automated backend and frontend tests.

## Known limitations

- The analyzer checks URL structure only. It does not verify DNS, TLS certificates, page contents, reputation feeds, or whether a site is currently malicious.
- A low score means only that these specific patterns were not found; it is not proof that a site is safe.
- Rate limits are in-memory and process-local. A multi-worker or horizontally scaled production deployment should use a shared rate-limit store.
- Account verification, password reset, MFA, and administrative review workflows are not included in this educational first version.
- Do not use CyberShield as an incident-response, compliance, or production threat-intelligence system.
