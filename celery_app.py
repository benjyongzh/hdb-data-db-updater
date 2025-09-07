import os
from celery import Celery
from celery.signals import worker_ready
from common.temp_cleanup import cleanup_resale_temp_files


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery = Celery(
    "hdb_data_db_updater",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Reasonable defaults; adjust concurrency/acks_late as needed
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    include=["tasks.jobs"],  # ensure worker imports our task module
    # Reduce Redis polling frequency: worker blocks up to N seconds
    broker_transport_options={
        # Default BRPOP timeout is ~1s; make it configurable with env
        "brpop_timeout": int(os.getenv("REDIS_BRPOP_TIMEOUT", "10")),
    },
)


@celery.task(bind=True)
def ping(self):
    return {"status": "ok"}


@worker_ready.connect
def _cleanup_tmp_on_worker_ready(**kwargs):
    """Fail-safe: clean leftover temp files when the worker becomes ready."""
    try:
        cleanup_resale_temp_files()
    except Exception:
        pass

