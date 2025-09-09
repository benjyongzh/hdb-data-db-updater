from fastapi import APIRouter
from celery_app import celery
from common.response import success_response, error_response


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}")
def get_task_status(task_id: str):
    try:
        res = celery.AsyncResult(task_id)
        info = res.info if isinstance(res.info, dict) else {"detail": str(res.info)}
        payload = {
            "task_id": task_id,
            "state": res.state,
            "ready": res.ready(),
            "successful": res.successful() if res.ready() else None,
            "result": info if res.ready() and res.successful() else None,
        }
        return success_response(payload)
    except Exception as e:
        return error_response(500, str(e))

