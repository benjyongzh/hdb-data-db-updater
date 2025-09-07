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

**Background Jobs (Celery)**
- Broker/backend: Redis. Set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` in `.env` (see `.env.example`).
- Start a worker:
  - `celery -A celery_app.celery worker -l info`
- Enqueued POST endpoints return a `task_id`.
- Query status: `GET /api/tasks/{task_id}` → `{ task_id, state, ready, successful, result }`.
 - Run Redis locally:
   - Native install, or via Docker: `docker run -p 6379:6379 redis:7`

**Endpoints**
- Root: `GET /` — service banner.
- Health: `GET /health` — returns `{ "status": "ok" }`.

Resale Transactions
- List: `GET /api/resale-transactions/`
  - Query: `town`, `block`, `flat_type`, `min_price`, `max_price`, `limit` (default 100), `offset` (default 0)
- Get by ID: `GET /api/resale-transactions/{id}`
- Refresh table (non-blocking): `POST /api/resale-transactions/refresh` → `{ task_id }`

Postal Codes
- List: `GET /api/postal-codes/`
  - Query: `block`, `street_name`, `postal_code`, `limit`, `offset`
- Get by ID: `GET /api/postal-codes/{id}`
- Reset: `POST /api/postal-codes/reset?mode=clear-links|clear-table`
 - Link resale FKs (non-blocking): `POST /api/postal-codes/link-resale` → `{ task_id }`

Building Polygons
- List: `GET /api/building-polygons/`
  - Query: `block`, `postal_code`, `limit`, `offset`
- Get by ID: `GET /api/building-polygons/{id}`
- Refresh table (non-blocking): `POST /api/building-polygons/refresh` → `{ task_id }`

Rail Stations
- List: `GET /api/rail-stations/`
  - Query: `name`, `ground_level`, `limit`, `offset`
- Get by ID: `GET /api/rail-stations/{id}`
- Refresh table (non-blocking): `POST /api/rail-stations/refresh` → `{ task_id }`

Rail Lines
- List: `GET /api/rail-lines/`
  - Query: `name`, `abbreviation`, `rail_type`, `limit`, `offset`
- Get by ID: `GET /api/rail-lines/{id}`
- Refresh table (non-blocking): `POST /api/rail-lines/refresh` → `{ task_id }`

Table Metadata
- List: `GET /api/table-metadata/`
  - Query: `limit`, `offset`
- Get by ID: `GET /api/table-metadata/{id}`
- Touch (create/update timestamp): `POST /api/table-metadata/touch`
  - Body: `{ "table_id": number }` or `{ "table_name": string }` (provide exactly one)

Examples
- `curl "http://localhost:8000/api/resale-transactions/?town=ANG%20MO%20KIO&limit=5"`
- `curl -X POST http://localhost:8000/api/rail-lines/refresh`
- `curl http://localhost:8000/api/tasks/<task_id>`

**Data Model**
- Core tables and relationships (simplified):

```
postal_codes (id PK)
  - block TEXT
  - street_name TEXT
  - postal_code TEXT

resale_transactions (id PK)
  - month, town, flat_type, block, street_name, ...
  - postal_code_key_id INTEGER NULL -> postal_codes.id (FK)

building_polygons (id PK)
  - block TEXT, postal_code TEXT
  - postal_code_key_id INTEGER NULL -> postal_codes.id (FK)
  - building_polygon geometry(Polygon, 4326)

rail_lines (id PK)
  - name, abbreviation (UNIQUE), rail_type, colour

rail_stations (id PK)
  - name, ground_level, building_polygon geometry(Polygon, 4326)

rail_stations_lines (mrt_station_id, line_id) PK
  - mrt_station_id -> rail_stations.id (FK)
  - line_id -> rail_lines.id (FK)

data_tables (id PK)
  - name UNIQUE

table_metadata (id PK)
  - table_id UNIQUE -> data_tables.id (FK)
  - created_at, updated_at
```

**POST Flows**
- `POST /api/resale-transactions/refresh`
  - Downloads latest CSV via data.gov.sg URL.
  - Creates temp staging table and bulk COPYs CSV.
  - Truncates `resale_transactions` and inserts from staging.
  - Links all resale rows to `postal_codes` (existing first, then creates missing via OneMap).
  - Touches `table_metadata` for the target table.

- `POST /api/building-polygons/refresh`
  - Fetches GeoJSON dataset, strips Z coordinates.
  - Parses feature descriptions for block and postal code.
  - Truncates `building_polygons` and inserts rows (with geometry).
  - Touches `table_metadata` for the table.

- `POST /api/rail-stations/refresh`
  - Fetches stations GeoJSON, strips Z coordinates.
  - Parses description for `NAME` and `GRND_LEVEL`.
  - Truncates `rail_stations` and inserts rows (with geometry).
  - Rebuilds `rail_stations_lines` mappings using static line assignments.
  - Touches `table_metadata` for the table.

- `POST /api/rail-lines/refresh`
  - Rebuilds `rail_lines` entirely from static mapping (name, abbreviation, rail_type, colour).
  - Truncates and inserts rows.
  - Touches `table_metadata` for the table.

- `POST /api/table-metadata/touch`
  - Ensures the logical table exists in `data_tables`.
  - Upserts `table_metadata` row; updates `updated_at`.

- `POST /api/postal-codes/link-resale`
  - Detects FK column on `resale_transactions` (postal_code_key_id/id/key).
  - Bulk-links rows with existing `postal_codes` matches.
  - For remaining `(block, street_name)` pairs, queries OneMap for a postal code, inserts into `postal_codes`, and links all matching resale rows.

- `POST /api/postal-codes/reset?mode=clear-links|clear-table`
  - `clear-links`: NULLs the postal code FK on all `resale_transactions`.
  - `clear-table`: NULLs the FK, then truncates `postal_codes` and resets identity.

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
 - CELERY_BROKER_URL: Redis URL for Celery broker (default `redis://localhost:6379/0`).
 - CELERY_RESULT_BACKEND: Redis URL for Celery result backend (default `redis://localhost:6379/1`).
