# hdb-data-db-updater
Gets HDB data via shell scripts on anacron. Uses data to update a PostgreSQL DB.

**Using uv (recommended)**
- Prerequisite: Install `uv` from Astral.
  - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows (PowerShell): `irm https://astral.sh/uv/install.ps1 | iex`
  - Docs: https://docs.astral.sh/uv/
- Create virtual environment: run `uv venv` in the project root (creates `.venv`).
- Activate virtual environment:
  - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
  - Windows CMD: `.\.venv\Scripts\activate.bat`
  - Windows Git Bash: `cd .venv/Scripts && . activate && cd ../..`
  - macOS/Linux: `source .venv/bin/activate`
- Install dependencies (from pinned `requirements.txt`): `uv pip sync requirements.txt`
  - Alternatively: `uv pip install -r requirements.txt`
- Optional (no manual activation): prefix commands with `uv run`, for example:
  - `uv run python main.py`
  - `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

Notes
- Python version: Use a Python 3.10+ interpreter. If needed, you can direct `uv` to use/install a specific version, e.g. `uv run --python 3.10 python --version`.
- The `.venv/` folder is already ignored by `.gitignore`.

**Start the app**
- Install runtime deps (if not yet installed): `uv pip install fastapi uvicorn`
- Start with autoreload (recommended for dev): `uv run python main.py`
- Alternate start: `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
- Health check: visit `http://localhost:8000/health` (returns `{ "status": "ok" }`).
