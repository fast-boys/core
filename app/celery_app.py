import os
from celery import Celery, shared_task
from dotenv import load_dotenv
import hvac
import numpy as np

from database import get_db
from models import user, plan, user_plan, visit_place, spot, city, article, my_spot, url
from models.url import Url

load_dotenv()
vault_token = os.getenv("VAULT_TOKEN")


vault_client = hvac.Client(
    url="http://j10d204.p.ssafy.io:8200",
    token=vault_token,
)

env_keys = vault_client.read("fastapi/data/path")["data"]["data"]
CELERY_REDIS = env_keys["CELERY_REDIS"]

# Celery 애플리케이션 생성
celery_core = Celery(
    "core_worker",
    broker=f"{CELERY_REDIS}/0",
    backend=f"{CELERY_REDIS}/1",
    include=["app.celery_app"],
)
celery_core.autodiscover_tasks()
celery_core.conf.task_default_queue = "core_to_ai_queue"


@shared_task(name="core_worker.process_data", queue="ai_to_core_queue")
def process_data(data: dict):
    # get_db() 제너레이터에서 DB 세션 인스턴스를 얻기
    db = next(get_db())

    try:
        # ai_worker의 연산 결과 조회
        url_id = data["url_id"]
        vector = data["vector"]

        # URL 정보 업데이트
        url_to_update = db.query(Url).filter(Url.id == url_id).first()
        if url_to_update is None:
            raise ValueError("url_id 정보가 없습니다.")

        url_to_update.status = True
        vector = np.array(vector, dtype=float)
        url_to_update.vector = vector.tobytes()
        db.commit()  # 변경 사항을 DB에 커밋
    finally:
        db.close()  # DB 세션 닫기

    return {"url_id": url_id}


if __name__ == "__main__":
    celery_core.worker_main(
        argv=[
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--queues=ai_to_core_queue",
        ]
    )
