# Improvement Tasks Checklist

## Backend: Configuration and Data
- [ ] Adopt a centralized configuration module using pydantic-settings; load DATABASE_URL, CORS origins, log level, scheduler toggle from env (.env).
- [ ] Replace hardcoded SQLite URL in backend\db.py with configuration-driven DATABASE_URL and create_engine kwargs (echo from config).
- [ ] Introduce context-managed DB sessions: expose dependency that yields Session in a with block to ensure closing.
- [ ] Add Alembic migrations and an initial migration for the Task table; document migration workflow.
- [ ] Add created_at and updated_at timestamp fields to Task, auto-managed in models and via DB default/SQLModel events.
- [ ] Enforce timezone-aware datetimes: store UTC; validate incoming due_at to coerce/assume UTC; always return ISO8601 with Z.
- [ ] Convert get_session() to a generator dependency that yields a session and commits/rolls back appropriately.
- [ ] Abstract time source (Clock/now provider) to ease testing of scheduler and due logic.
- [ ] Replace magic numbers (sleep intervals) with named constants in config.
- [ ] Introduce feature flags for optional behaviors (e.g., reminders, notifications) via config.

## Backend: API Design and Services
- [ ] Implement pagination for GET /tasks with limit/offset parameters and sensible defaults/max caps.
- [ ] Add filtering/sorting query params (completed, due_before, due_after, order_by) to GET /tasks.
- [ ] Validate TaskCreate: non-empty trimmed title; optional max length; reject titles of only whitespace.
- [ ] Validate TaskUpdate to prevent no-op empty payloads; return 400 if no fields provided.
- [ ] Standardize error responses with a consistent schema; include error codes and messages.
- [ ] Add OpenAPI enhancements: tags, response examples, error schemas, summary/description for each route.
- [ ] Introduce dependency-injected services layer (TaskService) to keep FastAPI routes thin and improve testability.
- [ ] Add repository layer functions for Task CRUD and queries; keep SQL in one place.
- [ ] Add bulk APIs: bulk create, bulk update completed flags for multiple tasks.
- [ ] Add data export/import endpoints (JSON) and corresponding frontend actions (optional).
- [ ] Add validation on delete to return 204 consistently and ensure idempotent behavior.

## Scheduler and WebSocket Alerts
- [ ] Parameterize scheduler interval and enable/disable via config; default to disabled for tests.
- [ ] Make reminder scheduler lifecycle-aware: graceful startup/shutdown, cancellation handling, and resource cleanup.
- [ ] Remove in-memory _sent_reminders global; determine reminder emission by querying due and not-notified tasks or by persisting last_notified_at.
- [ ] Add idempotency for reminder notifications to avoid duplicates across restarts.
- [ ] Improve WebSocket manager: send periodic ping/pong, prune dead connections, and log connection events.
- [ ] Consider authenticating WebSocket connections (token query/header) and authorizing messages (future-ready).

## Observability, Logging, and Health
- [ ] Add structured logging (loguru or stdlib logging) with request/response middleware; configure levels via settings.
- [ ] Replace broad exception swallowing in reminder_scheduler with logged exceptions and backoff; include traceback.
- [ ] Add health endpoints: GET /health (liveness) and GET /ready (readiness checks DB connectivity).
- [ ] Ensure uvicorn logging integrates with structured logging and includes request IDs; propagate request ID in responses.
- [ ] Add /version endpoint and embed git SHA/build timestamp (injected at build time).
- [ ] Add OpenTelemetry-ready hooks or metrics (prometheus-fastapi-instrumentator) for basic API metrics.
- [ ] Add error monitoring integration hooks (Sentry) behind a config flag (disabled by default).

## Security and Hardening
- [ ] Tighten CORS: configure allow_origins from settings; default to localhost dev values only.
- [ ] Add rate limiting and request size limits at the FastAPI level or behind a proxy (optional stretch).
- [ ] Review CORS and security headers (Starlette middleware for SecurityMiddleware) and configure for prod.

## Frontend (Kivy): Architecture, UX, and Networking
- [ ] Extract frontend API client into a separate module (frontend-kivy\api_client.py) to encapsulate HTTP calls.
- [ ] Switch frontend to use httpx.AsyncClient and schedule awaits with asyncio.create_task and Kivy Clock where needed.
- [ ] Remove direct asyncio.run calls from UI thread; use async tasks and @mainthread methods for UI updates.
- [ ] Close HTTP client(s) on app stop; add proper lifecycle hooks (on_start/on_stop) for resource management.
- [ ] Parameterize API_BASE and WS_URL via env file or config module; read from environment with sensible defaults.
- [ ] Add retry/backoff for HTTP operations (create, toggle, delete) and show user feedback on failures.
- [ ] Add input validation and UX improvements (date/time picker or clearer ISO hint/formatting).
- [ ] Improve list rendering: show completed status with a checkbox and separate column for due date; allow sorting.
- [ ] Add a simple state/store class for the frontend to decouple UI from data fetching (MVVM-like separation).
- [ ] Add WebSocket reconnection jitter/backoff and exponential delay; surface notifications to UI log.
- [ ] Ensure notification errors are handled gracefully; fall back to in-app toast/log if plyer is unavailable.
- [ ] Add logging in the frontend using Kivy's Logger; gate verbosity via env.
- [ ] Add typing annotations across frontend modules and enable mypy for frontend.
- [ ] Add optimistic UI updates in frontend with rollback on error for toggle/delete.
- [ ] Introduce pagination UI in frontend to match backend; load more button or infinite scroll.
- [ ] Add accessibility improvements in UI (labels, focus order, keyboard navigation).
- [ ] Normalize date formatting in frontend consistently (always localize or always UTC with clear label).

## Testing and Quality Assurance
- [ ] Add unit tests for backend services and repositories using a transient SQLite database in memory or tmp file.
- [ ] Add API tests using FastAPI TestClient covering CRUD, validation errors, pagination and filters.
- [ ] Add unit tests for the frontend API client (using respx to mock httpx) without spinning up UI.
- [ ] Expand frontend headless test to cover toggle and delete flows against a test server.
- [ ] Implement E2E tests: spin up FastAPI app in-process and run headless frontend flows against it.
- [ ] Add CI artifacts: test coverage report; enforce coverage threshold for backend tests.
- [ ] Add graceful shutdown tests ensuring background tasks terminate within timeout.

## CI/CD and Project Tooling
- [ ] Introduce typing and mypy strict-ish configuration; ensure backend passes static type checks.
- [ ] Add ruff and black to enforce linting and formatting; supply config files and pre-commit hooks.
- [ ] Add pre-commit configuration wiring ruff, black, mypy and simple safety checks.
- [ ] Create GitHub Actions CI workflow to run lint, type-check, and tests for backend and frontend.
- [ ] Consolidate environment management: provide environment.yml/requirements.txt and pin critical versions.
- [ ] Add Makefile or PowerShell scripts for common tasks (run server, run frontend, test, lint, format).
- [ ] Provide Windows-friendly PowerShell scripts (scripts\*.ps1) mirroring shell scripts for dev tasks.
- [ ] Add dependency vulnerability scanning (pip-audit or safety) in CI.

## Performance and Caching
- [ ] Add DB indexes for frequent queries (Task.completed, Task.due_at) to speed up reminders and listing.
- [ ] Add cache headers or ETags for list endpoints where applicable (if later backed by CDN).
- [ ] Add SQLite pragmas (journal_mode=WAL, synchronous=NORMAL) via create_engine for better dev performance.

## Deployment and Operations
- [ ] Add Dockerfile for backend (uvicorn) and docker-compose to run API with SQLite volume; document usage.
- [ ] Containerize frontend for reproducible packaging runs (optional).
- [ ] Document deployment options (uvicorn, systemd, Docker, Render/Fly/Heroku) and environment variables.
- [ ] Add database seed script for demo data and a script to reset the DB in dev/test.

## Documentation
- [ ] Add CONTRIBUTING.md detailing dev setup, code style, testing and release process.
- [ ] Improve README with architecture overview, diagrams (request/WS flows), and quick-start instructions.
- [ ] Add SECURITY.md with supported versions and vulnerability reporting process.
- [ ] Add code owners and CODE_OF_CONDUCT.md for community contributions (optional).
