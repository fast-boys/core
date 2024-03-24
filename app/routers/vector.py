from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from config.celery_config import celery_app

router = APIRouter()


@router.post("/process/")
def process_text(raw_text: str):
    # Celery를 통해 비동기 작업 실행
    task = celery_app.send_task('process_text', args=[raw_text])
    return {"task_id": task.id}


@router.get("/result/{task_id}")
def get_result(task_id: str):
    # Celery 작업 결과 조회
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {"status": task_result.status, "result": task_result.result}
    else:
        return {"status": "Processing", "result": None}
