from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from starlette.requests import Request
from common.response import error_response
from common.temp_cleanup import cleanup_resale_temp_files
from fastapi.middleware.cors import CORSMiddleware
from resale_transactions.resale_transaction_controller import router as resale_tx_router
from postal_codes.postal_code_controller import router as postal_codes_router
from building_polygons.building_polygon_controller import router as building_polygons_router
from rail_stations.rail_station_controller import router as rail_stations_router
from rail_lines.rail_line_controller import router as rail_lines_router
from table_metadata.table_metadata_controller import router as table_metadata_router
from tasks.tasks_controller import router as tasks_router


app = FastAPI(title="hdb-data-db-updater", root_path="/api")

# CORS configuration
config = dotenv_values(".env")
origins_str = (config.get("CORS_ORIGINS", "*") if isinstance(config, dict) else "*")
origins = [o.strip() for o in origins_str.split(",")] if origins_str and origins_str != "*" else ["*"]

# If allowing all origins, do not allow credentials to comply with CORS spec
allow_credentials = False if origins == ["*"] else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "HDB Data DB Updater API"}


@app.get("/health")
def health():
    return {"status": "ok"}


# Mount routers
app.include_router(resale_tx_router)
app.include_router(postal_codes_router)
app.include_router(building_polygons_router)
app.include_router(rail_stations_router)
app.include_router(rail_lines_router)
app.include_router(table_metadata_router)
app.include_router(tasks_router)


if __name__ == "__main__":
    # Local dev entrypoint: uvicorn with reload
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)

# Exception handlers to standardize error responses for all endpoints
@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    return error_response(422, "Validation error", code=42201, data={"errors": exc.errors()})


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    # Use provided status code and detail message
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return error_response(exc.status_code, message)


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    return error_response(500, "Internal server error", code=50000)


@app.on_event("startup")
async def cleanup_tmp_on_startup():
    # Best-effort cleanup of leftover temp files on API start
    try:
        cleanup_resale_temp_files()
    except Exception:
        pass
