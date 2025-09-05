import psycopg2
from dotenv import dotenv_values
from fastapi import FastAPI
from resale_transactions.resale_transaction_controller import router as resale_tx_router
from postal_codes.postal_code_controller import router as postal_codes_router
from building_polygons.building_polygon_controller import router as building_polygons_router
from mrt_stations.mrt_station_controller import router as mrt_stations_router


app = FastAPI(title="hdb-data-db-updater")


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
app.include_router(mrt_stations_router)


if __name__ == "__main__":
    # Local dev entrypoint: uvicorn with reload
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
