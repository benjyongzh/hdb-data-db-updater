from fastapi import APIRouter, HTTPException
from celery_app import celery


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/{task_id}")
def get_task_status(task_id: str):
    try:
        res = celery.AsyncResult(task_id)
        info = res.info if isinstance(res.info, dict) else {"detail": str(res.info)}
        return {
            "task_id": task_id,
            "state": res.state,
            "ready": res.ready(),
            "successful": res.successful() if res.ready() else None,
            "result": info if res.ready() and res.successful() else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

