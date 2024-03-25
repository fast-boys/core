from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
import os
from dotenv import load_dotenv

from vault_client import get_env_value
from schemas.spot_dto import SimpleSpotDto
from services.recommend import extract_similar_spots
from services.utils import get_internal_id
from database import get_es_client, get_m_db

router = APIRouter(tags=["recommendation"], prefix="/recommendation")

index_name = get_env_value("INDEX_NAME")


@router.get(path="/{spot_id}/global", response_model=List[SimpleSpotDto])
async def get_similar_by_spot_id_in_global(
    spot_id: str,
    es: Any = Depends(get_es_client),
    collection: Any = Depends(get_m_db),
):
    """
    관광지의 Id를 받아 유사한 관광지를 10개 반환합니다.

    아래의 입력을 받아 반환합니다.
    - :param **spot_id**: 관광지 식별자
    - :return **List[SimpleSpotDto]**: 유사한 관광지 리스트 반환
    """
    try:  # 1. spot_id 의 주소와 벡터 반환
        response = es.search(
            index=index_name, body={"query": {"match": {"spot_id": spot_id}}, "_source": ["text_vector"]}
        )
        if not response["hits"]["hits"]:  # 검색 결과가 비어 있는 경우
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 해당 spot의 text_vector
    spot_vector = response.get("hits").get("hits")[0].get("_source").get("text_vector")
    knn_query = {
        "knn": {"field": "text_vector", "query_vector": spot_vector, "k": 11, "num_candidates": 100},
        "fields": ["name", "spot_id"],
        "size": 11,
    }

    try:  # 2. 벡터 기준 유사한 k개 관광지 반환
        knn_response = es.search(index=index_name, body=knn_query)
        if not knn_response["hits"]["hits"]:  # 검색 결과가 비어 있는 경우
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 유사한 장소들 추출
    similar_spots = extract_similar_spots(knn_response, collection)

    # 유사한 관광지가 없는 경우 예외 발생
    if not similar_spots:
        raise HTTPException(status_code=404, detail="유사한 관광지를 찾을 수 없습니다.")

    return similar_spots


@router.get(path="/{spot_id}/local", response_model=List[SimpleSpotDto])
async def get_similar_by_spot_id_in_local(
    spot_id: str,
    es: Any = Depends(get_es_client),
    collection: Any = Depends(get_m_db),
):
    """
    관광지의 Id를 받아 유사한 관광지를 10개 반환합니다.
    이때, 해당 spot의 주소와 대조하여 가장 유사도가 높은 결과를 반환합니다.

    아래의 입력을 받아 반환합니다.
    - :param **spot_id**: 관광지 식별자
    - :return **List[SimpleSpotDto]**: 유사한 관광지 리스트 반환
    """
    try:
        response = es.search(
            index=index_name, body={"query": {"match": {"spot_id": spot_id}}, "_source": ["text_vector", "address"]}
        )
        if not response["hits"]["hits"]:  # 검색 결과가 비어 있는 경우
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    spot_vector = response.get("hits").get("hits")[0].get("_source").get("text_vector")
    spot_addr = response.get("hits").get("hits")[0].get("_source").get("address")
    # 좌표값 기준 후처리 필요하지만, 당장은 구현상 어려움으로 사용하지 않음
    # spot_lat = response.get("hits").get("hits")[0].get("_source").get("location").get("lat")
    # spot_lon = response.get("hits").get("hits")[0].get("_source").get("location").get("lon")

    knn_query = {
        "query": {
            "match": {
                "address": {
                    "query": spot_addr,
                }
            }
        },
        "knn": {"field": "text_vector", "query_vector": spot_vector, "k": 11, "num_candidates": 100},
        "size": 11,
    }

    try:
        knn_response = es.search(index=index_name, body=knn_query)
        if not knn_response["hits"]["hits"]:  # 검색 결과가 비어 있는 경우
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 유사한 장소들 추출
    similar_spots = extract_similar_spots(knn_response, collection)

    # 유사한 관광지가 없는 경우 예외 발생
    if not similar_spots:
        raise HTTPException(status_code=404, detail="유사한 관광지를 찾을 수 없습니다.")

    return similar_spots
