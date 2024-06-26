from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
import numpy as np

from vault_client import get_env_value
from schemas.spot_dto import SimpleSpotDto, LocationRequestDto
from services.recommend import extract_similar_spots
from services.profile import get_internal_id
from database import get_es_client, get_db, get_m_db
from models.user import User

router = APIRouter(tags=["recommendation"], prefix="/recommendation")

index_name = get_env_value("ES_IDX_NAME")


@router.get(path="/", response_model=List[SimpleSpotDto])
async def get_recommendations(
        internal_id: str = Depends(get_internal_id),
        db: Any = Depends(get_db),
        es: Any = Depends(get_es_client),
        collection: Any = Depends(get_m_db),
):
    """
    해당 유저의 사용자 벡터를 기반으로 추천 관광지를 10개 반환합니다.

    - :param **internal_id**: 사용자 내부 아이디 (HEADER)
    - :return **List[SimpleSpotDto]**: 유사한 관광지 리스트 반환
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    user_vector = user.vector
    user_vector = np.frombuffer(user_vector, dtype=float)
    user_vector = np.nan_to_num(user_vector)
    # print(len(user_vector))   # 768

    # user_vector 기준으로 유사도 검색
    knn_query = {
        "knn": {
            "field": "text_vector",
            "query_vector": user_vector.tolist(),
            "k": 11,
            "num_candidates": 100,
        },
        "fields": ["name", "spot_id"],
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


@router.post(path="/location", response_model=List[SimpleSpotDto])
async def get_recommendations(
        request: LocationRequestDto,
        internal_id: str = Depends(get_internal_id),
        db: Any = Depends(get_db),
        es: Any = Depends(get_es_client),
        collection: Any = Depends(get_m_db),
):
    """
    해당 유저의 사용자 벡터를 기반으로 추천 관광지를 10개 반환합니다.

    추가 조건으로 사용자의 위치 기반 10km 이내 관광지를 추천합니다.

    (구미시,36.110336, 128.411238)

    - :param **internal_id**: 사용자 내부 아이디 (HEADER)
    - :return **List[SimpleSpotDto]**: 유사한 관광지 리스트 반환
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    user_vector = user.vector
    user_vector = np.frombuffer(user_vector, dtype=float)
    user_vector = np.nan_to_num(user_vector)

    # user_vector 기준으로 유사도 검색
    knn_query = {
        "knn": {
            "field": "text_vector",
            "query_vector": user_vector.tolist(),
            "k": 11,
            "num_candidates": 100,
            "filter": {
                "geo_distance": {
                    "distance": "10km",  # 10km 이내의 결과만 필터링
                    "location": {
                        "lat": request.lat,
                        "lon": request.long,
                    },
                }
            },
        },
        "fields": ["name", "spot_id"],  # 반환할 필드 지정
        "size": 11,  # 반환할 문서의 최대 개수
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
            index=index_name,
            body={"query": {"match": {"spot_id": spot_id}}, "_source": ["text_vector"]},
        )
        if not response["hits"]["hits"]:  # 검색 결과가 비어 있는 경우
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 해당 spot의 text_vector
    spot_vector = response.get("hits").get("hits")[0].get("_source").get("text_vector")
    knn_query = {
        "knn": {
            "field": "text_vector",
            "query_vector": spot_vector,
            "k": 11,
            "num_candidates": 100,
        },
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
            index=index_name,
            body={
                "query": {"match": {"spot_id": spot_id}},
                "_source": ["text_vector", "address"],
            },
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
        "knn": {
            "field": "text_vector",
            "query_vector": spot_vector,
            "k": 11,
            "num_candidates": 100,
        },
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


@router.get(path="/best_list", response_model=List[SimpleSpotDto])
async def get_best_list(
        db: Any = Depends(get_db),
        es: Any = Depends(get_es_client),
        collection: Any = Depends(get_m_db),
):
    """
    실시간 인기 여행지를 보여줍니다 (더미데이터)

    - :param **internal_id**: 사용자 내부 아이디 (HEADER)
    - :return **List[SimpleSpotDto]**: 유사한 관광지 리스트 반환
    """

    # 미구현, 일단 랜덤으로 관광지 리턴
    rand_query = {
        "query": {
            "terms": {
                "spot_id": [
                    "1032715",
                    "1008185",
                    "1022231",
                    "1051766",
                    "1013441",
                    "1013527",
                    "1002006",
                    "1034361",
                    "125583",
                    "126230"
                ]
            }
        },
        "size": 10,
        "_source": ["name", "spot_id"]
    }

    try:
        response = es.search(index=index_name, body=rand_query)
        if not response["hits"]["hits"]:  # 검색 결과가 비어 있는 경우
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 유사한 장소들 추출
    similar_spots = extract_similar_spots(response, collection)
    return similar_spots
