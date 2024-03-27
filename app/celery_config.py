import os
from celery import Celery, shared_task
from dotenv import load_dotenv
import hvac

load_dotenv()
vault_token = os.getenv("VAULT_TOKEN")


vault_client = hvac.Client(
    url="http://j10d204.p.ssafy.io:8200",
    token=vault_token,
)

env_keys = vault_client.read("fastapi/data/path")["data"]["data"]

CELERY_REDIS = env_keys["CELERY_REDIS"]

# Celery 애플리케이션 생성
celery_app = Celery(
    "core",
    broker=f"{CELERY_REDIS}/0",  # Redis를 브로커로 사용하는 경우
    backend=f"{CELERY_REDIS}/1",  # 결과 백엔드로 Redis를 사용
)

celery_app.conf.task_routes = {"process_data": {"queue": "main-queue"}}
celery_app.conf.task_default_queue = "main-queue"


@shared_task(name="process_data")
def process_data(data):
    print(f"Processing data: {data}")
    return data
