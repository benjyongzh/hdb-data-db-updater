import os
from celery import Celery
import logging
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
def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


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
        "brpop_timeout": int(os.getenv("REDIS_BRPOP_TIMEOUT", "60")),
        # How often Kombu sends health-check PINGs to Redis
        "health_check_interval": int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "60")),
    },
    # Cap connections to the broker
    broker_pool_limit=int(os.getenv("BROKER_POOL_LIMIT", "2")),
    # Slow worker heartbeats/events to once per 60s
    worker_heartbeat=int(os.getenv("WORKER_HEARTBEAT", "60")),
    # Minimize events/remote control chatter by default (can be overridden via env)
    worker_send_task_events=_env_bool("WORKER_SEND_TASK_EVENTS", False),
    task_send_sent_event=_env_bool("TASK_SEND_SENT_EVENT", False),
    worker_enable_remote_control=_env_bool("WORKER_ENABLE_REMOTE_CONTROL", False),
)

# Log key broker/worker settings on import/worker boot
try:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__).info(
        "Celery broker_transport_options=%s broker_pool_limit=%s worker_heartbeat=%s events=%s sent_event=%s remote_control=%s",
        celery.conf.broker_transport_options,
        celery.conf.broker_pool_limit,
        celery.conf.worker_heartbeat,
        celery.conf.worker_send_task_events,
        celery.conf.task_send_sent_event,
        celery.conf.worker_enable_remote_control,
    )
except Exception:
    # Fallback print if logging fails very early
    print(
        "Celery broker_transport_options=",
        celery.conf.broker_transport_options,
        " broker_pool_limit=",
        celery.conf.broker_pool_limit,
        " worker_heartbeat=",
        celery.conf.worker_heartbeat,
        " events=",
        celery.conf.worker_send_task_events,
        " sent_event=",
        celery.conf.task_send_sent_event,
        " remote_control=",
        celery.conf.worker_enable_remote_control,
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

