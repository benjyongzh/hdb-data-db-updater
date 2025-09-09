from __future__ import annotations

from typing import Any, Dict

from celery_app import celery

from resale_transactions.resale_transaction_service import (
    refresh_resale_transaction_table,
)
from building_polygons.building_polygon_service import (
    refresh_building_polygon_table,
    link_all_building_polygons_to_postal_codes,
)
from rail_stations.rail_station_service import (
    refresh_rail_stations_table,
)
from rail_lines.rail_line_service import (
    refresh_rail_lines_table,
)
from postal_codes.postal_code_service import (
    link_all_resale_transactions_to_postal_codes,
)


@celery.task(name="refresh_resale_transactions")
def refresh_resale_transactions_task() -> Dict[str, Any]:
    inserted = refresh_resale_transaction_table()
    # Link all resale transactions to postal codes as part of the refresh
    link_summary = link_all_resale_transactions_to_postal_codes()
    return {"inserted": inserted, "link_summary": link_summary}


@celery.task(name="refresh_building_polygons")
def refresh_building_polygons_task() -> Dict[str, Any]:
    count = refresh_building_polygon_table()
    linked = link_all_building_polygons_to_postal_codes()
    return {"inserted": count, "linked": linked}


@celery.task(name="refresh_rail_stations")
def refresh_rail_stations_task() -> Dict[str, Any]:
    count = refresh_rail_stations_table()
    return {"inserted": count}


@celery.task(name="refresh_rail_lines")
def refresh_rail_lines_task() -> Dict[str, Any]:
    count = refresh_rail_lines_table()
    return {"inserted": count}


@celery.task(name="link_resale_to_postal_codes")
def link_resale_to_postal_codes_task() -> Dict[str, Any]:
    summary = link_all_resale_transactions_to_postal_codes()
    return summary

