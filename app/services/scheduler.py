from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import numpy as np
from apscheduler.triggers.cron import CronTrigger
from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session

from vault_client import get_env_value
from models.my_spot import MySpot
from models.user import User
from database import get_es_client, get_db

db_url = get_env_value("DATABASE_URL")
index_name = get_env_value("ES_IDX_NAME")


# spot_id를 통해 개별 관광지의 vector를 조회
def get_vector_by_spot_id(spot_id: str, es_client: Elasticsearch):
    response = es_client.search(
        index=index_name, body={"query": {"match": {"spot_id": spot_id}}}
    )
    vector = response["hits"]["hits"][0]["_source"].get("vector", None)
    return vector


# db에서 가장 최근에 좋아요한 관광지 조회
def get_recent_likes(user_id: int, db: Session = get_db()):
    recent_likes = (
        db.query(MySpot)
        .filter(MySpot.user_id == user_id)
        .order_by(MySpot.created_date.desc())
        .limit(10)
        .all()
    )

    return recent_likes


# user_id와 my_spot을 비교
# my_spot이 10개 미만인 경우, 설문조사의 추천 상태를 유지
# 10개 이상인 경우, 가장 최근에 좋아요한 10개를 가져와서 사용자 벡터 갱신
def calculate_user_vector(user_id: int, es_client: Elasticsearch = get_es_client()):
    # 최근 순으로 좋아요 리스트 조회
    recent_likes = get_recent_likes(user_id)

    if len(recent_likes) < 10:
        return None

    vectors = []
    weights = np.arange(len(recent_likes), 0, -1)  # numpy 배열로 가중치 생성
    total_weight = np.sum(weights)

    for like, weight in zip(recent_likes, weights):
        vector = get_vector_by_spot_id(like.spot_id, es_client)
        if vector is not None:
            # 벡터를 numpy 배열로 변환하고 가중치 적용
            weighted_vector = np.array(vector) * weight
            vectors.append(weighted_vector)

    if not vectors:
        return None  # 벡터 정보가 없는 경우

    # 벡터 배열의 리스트를 하나의 numpy 배열로 결합
    vectors = np.stack(vectors)
    # 가중 평균 계산
    user_vector = np.sum(vectors, axis=0) / total_weight

    return user_vector.tolist()


# 모든 사용자의 벡터를 갱신하는 함수
def update_all_user_vectors():
    db = next(get_db())

    # 사용자 ID 리스트
    user_ids = [id for id, in db.query(User.id).yield_per(1000)]

    for user_id in user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        user_vector = calculate_user_vector(user_id)
        if user_vector is None:
            continue
        user.vector = user_vector
        db.commit()


# 스케줄러 인스턴스 생성
scheduler = AsyncIOScheduler()
scheduler.add_jobstore(SQLAlchemyJobStore(url=db_url), "default")


def start_scheduler():
    if not scheduler.running:
        # 매일 자정에 `update_all_user_vectors` 함수 실행
        scheduler.add_job(
            update_all_user_vectors,
            CronTrigger(hour=0, minute=0),
            id="update_user_vectors",
        )
        try:
            scheduler.start()
        except Exception as e:
            pass


def rollback_scheduler():
    try:
        scheduler.remove_job("update_user_vectors")
    except Exception as e:
        # 작업이 존재하지 않거나, 삭제 중 오류 발생 시
        pass
    finally:
        # 스케줄러 종료
        if scheduler.running:
            scheduler.shutdown()
