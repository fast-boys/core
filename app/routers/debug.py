from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from celery.result import AsyncResult
from celery import Celery

from vault_client import get_env_value

CELERY_REDIS = get_env_value("CELERY_REDIS")

router = APIRouter(tags=["Debugger"], prefix="/debug")


def get_core_worker():
    return Celery(
        "core_worker", broker=f"{CELERY_REDIS}/0", backend=f"{CELERY_REDIS}/1"
    )


@router.get("/result/{task_id}")
def get_result(task_id: str, celery: Any = Depends(get_core_worker)):
    """
    Celery 작업 결과 조회용 API
    """
    task_result = AsyncResult(task_id, app=celery)
    return {"status": task_result.status, "result": task_result.result}
