from typing import List
import numpy as np
from elasticsearch import Elasticsearch

from vault_client import get_env_value

index_name = get_env_value("ES_IDX_NAME")


# spot_id를 통해 개별 관광지의 vector를 조회
def get_vector_by_spot_id(spot_id: str, es_client: Elasticsearch):
    response = es_client.search(
        index=index_name, body={"query": {"match": {"spot_id": spot_id}}}
    )

    hits = response["hits"]["hits"]
    if not hits:
        raise Exception("Not Found spot_id")

    vector = hits[0]["_source"].get("text_vector")
    return vector


# 선택된 spot_id의 벡터 평균 리턴
def calculate_user_vector(
    survey_spots: List[str], es_client: Elasticsearch
) -> np.ndarray:
    vectors = []
    for spot_id in survey_spots:
        try:
            vector = get_vector_by_spot_id(spot_id, es_client)
            vectors.append(np.array(vector, dtype=float))
        except Exception as e:
            print(f"{spot_id} : {e}")
            continue  # 에러가 생긴 벡터 무시하고 진행

    # 모든 spot_id가 잘못된 경우, 기본 벡터 반환
    if not vectors:
        return np.zeros(768)

    user_vector = np.mean(vectors, axis=0)
    return user_vector
