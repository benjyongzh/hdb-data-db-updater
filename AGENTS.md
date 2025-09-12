# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: FastAPI app, CORS, routers, startup cleanup.
- `api/index.py`: Vercel serverless entrypoint to the FastAPI app.
- Feature modules: `resale_transactions/`, `postal_codes/`, `building_polygons/`, `rail_stations/`, `rail_lines/`, `table_metadata/`.
  - Pattern: `<feature>.py` (Pydantic models), `<feature>_service.py` (DB logic), `<feature>_controller.py` (routes, `APIRouter router`).
- `tasks/`: Celery jobs and task routes. `celery_app.py` configures the worker.
- `common/`: DB connection, responses, pagination, utilities.
- `sql/schema.sql`: PostgreSQL + PostGIS schema.
- Infra: `Dockerfile`, `vercel.json`, `fly.toml`, `.env.example`, `requirements.txt`.

## Build, Test, and Development Commands
- Create env: `uv venv` (or use `uv run` without manual activation).
- Install deps: `uv pip sync requirements.txt`.
- Run API (dev): `uv run python main.py` or `uv run uvicorn main:app --reload --port 8000`.
- Start Celery worker: `uv run celery -A celery_app.celery worker -l info`.
- Apply DB schema: `psql "$DB_URL" -f sql/schema.sql` (PowerShell: `psql $env:DB_URL -f sql/schema.sql`).
- Docker: `docker build -t hdb-updater .` then `docker run -p 8000:8000 --env-file .env hdb-updater`.

## Coding Style & Naming Conventions
- Python 3.10+; 4-space indentation; prefer type hints.
- Modules/paths: snake_case. Classes: PascalCase. Functions/vars: snake_case.
- Keep controllers thin; put DB logic in `*_service.py`; return standardized JSON via `common.response`.
- No enforced formatter; follow PEP 8. Optional tools: `ruff`, `black`.

## Testing Guidelines
- No formal suite yet. Use `pytest` with `tests/` and files named `test_*.py`.
- Prefer FastAPI `TestClient` for route tests and a disposable DB/schema.
- Run tests (if added): `uv run pytest -q`.

## Commit & Pull Request Guidelines
- Use clear prefixes when possible: `feat:`, `fix:`, `chore:`, `docs:`.
- Small, focused commits; reference issues (e.g., `Fixes #123`).
- PRs include: summary, rationale, affected endpoints, example `curl`, DB impact/migrations, and screenshots/logs where helpful.

## Security & Configuration Tips
- Configure via `.env` (see `.env.example`): `DB_URL`, `CORS_ORIGINS`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, and table overrides.
- Do not commit secrets. For dev Redis: `docker run -p 6379:6379 redis:7`.
- Ensure PostGIS is enabled; geometry columns are used in several tables.

## Agent-Specific Instructions
- Always update `README.md` when you add, change, or remove endpoints, env vars, commands, or behaviors. Include request/response shapes and example usage where applicable.
