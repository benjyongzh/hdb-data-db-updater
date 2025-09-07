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
  - `uv run uvicorn main:app --port 8000 --reload`

Notes
- Python version: Use a Python 3.10+ interpreter. If needed, you can direct `uv` to use/install a specific version, e.g. `uv run --python 3.10 python --version`.
- The `.venv/` folder is already ignored by `.gitignore`.

**Start the app**
- Install runtime deps (if not yet installed): `uv pip install fastapi uvicorn`
- Start with autoreload (recommended for dev): `uv run python main.py`
- Alternate start: `uv run uvicorn main:app --port 8000 --reload`
- Health check: visit `http://localhost:8000/health` (returns `{ "status": "ok" }`).

**Endpoints**
- Root: `GET /` — service banner.
- Health: `GET /health` — returns `{ "status": "ok" }`.

Resale Transactions
- List: `GET /api/resale-transactions/`
  - Query: `town`, `block`, `flat_type`, `min_price`, `max_price`, `limit` (default 100), `offset` (default 0)
- Get by ID: `GET /api/resale-transactions/{id}`
- Refresh table: `POST /api/resale-transactions/refresh`

Postal Codes
- List: `GET /api/postal-codes/`
  - Query: `block`, `street_name`, `postal_code`, `limit`, `offset`
- Get by ID: `GET /api/postal-codes/{id}`

Building Polygons
- List: `GET /api/building-polygons/`
  - Query: `block`, `postal_code`, `limit`, `offset`
- Get by ID: `GET /api/building-polygons/{id}`

Rail Stations
- List: `GET /api/rail-stations/`
  - Query: `name`, `ground_level`, `limit`, `offset`
- Get by ID: `GET /api/rail-stations/{id}`
- Refresh table: `POST /api/rail-stations/refresh`

Rail Lines
- List: `GET /api/rail-lines/`
  - Query: `name`, `abbreviation`, `rail_type`, `limit`, `offset`
- Get by ID: `GET /api/rail-lines/{id}`
- Refresh table: `POST /api/rail-lines/refresh`

Table Metadata
- List: `GET /api/table-metadata/`
  - Query: `limit`, `offset`
- Get by ID: `GET /api/table-metadata/{id}`
- Touch (create/update timestamp): `POST /api/table-metadata/touch`
  - Body: `{ "table_id": number }` or `{ "table_name": string }` (provide exactly one)

Examples
- `curl "http://localhost:8000/api/resale-transactions/?town=ANG%20MO%20KIO&limit=5"`
- `curl -X POST http://localhost:8000/api/rail-lines/refresh`

**Environment Variables**
- DB_HOST: PostgreSQL host (default `localhost`).
- DB_PORT: PostgreSQL port (default `5432`).
- DB_NAME: Database name (default `postgres`).
- DB_USER: Database user (default `postgres`).
- DB_PASSWORD: Database password (default empty).
- CORS_ORIGINS: Comma-separated origins for CORS (default `*`).
- BUILDING_POLYGONS_TABLE: Override table name for building polygons.
- POSTAL_CODES_TABLE: Override table name for postal codes.
- RAIL_STATIONS_TABLE: Override table name for rail stations.
- RAIL_LINES_TABLE: Override table name for rail lines (default `rail_lines`).
- RAIL_STATION_LINES_TABLE: Override join table name between stations and lines (default `<RAIL_STATIONS_TABLE>_lines`).
- RESALE_TRANSACTIONS_TABLE: Override table name for resale transactions.
- TABLE_METADATA_TABLE: Override table name for the metadata table.
- DATA_TABLES_TABLE: Override registry table name for data tables (default `data_tables`).
