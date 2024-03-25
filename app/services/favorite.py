import os
from datetime import datetime

import numpy as np
from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session

from models import my_spot
from database import get_es_client, get_m_db

# es_client = get_es_client()
index_name = os.getenv("INDEX_NAME")


# spot_id를 통해 개별 관광지의 vector를 조회
def get_vector_by_spot_id(spot_id: str, es_client: Elasticsearch):
    response = es_client.search(
        index=index_name, body={"query": {"match": {"spot_id": spot_id}}}
    )
    vector = response["hits"]["hits"][0]["_source"].get("vector", None)
    return vector


# db에서 가장 최근에 좋아요한 관광지 조회
def get_recent_likes(user_id: int, db: Session):
    recent_likes = (
        db.query(my_spot)
        .filter(my_spot.user_id == user_id)
        .order_by(my_spot.created_date.desc())
        .limit(10)
        .all()
    )
    return recent_likes


# user_id와
def calculate_user_vector(user_id: int, db: Session, es_client: Elasticsearch):
    # 최근 순으로 좋아요 리스트 조회
    recent_likes = get_recent_likes(user_id, db)

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
