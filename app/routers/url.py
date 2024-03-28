from datetime import datetime
import re
import requests
import numpy as np
from celery import Celery
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
from starlette import status

from services.url import fetch_og_data, delete_iframe, crawl_naver_blog
from services.profile import get_internal_id
from database import get_db, get_m_db, get_es_client
from models.url import Url
from models.user import User
from schemas.url_dto import UrlDto
from schemas.spot_dto import SimpleSpotDto
from vault_client import get_env_value

CELERY_REDIS = get_env_value("CELERY_REDIS")
index_name = get_env_value("ES_IDX_NAME")

router = APIRouter(tags=["User Url"], prefix="/url")


def get_core_worker():
    celery = Celery(
        "core_worker", broker=f"{CELERY_REDIS}/0", backend=f"{CELERY_REDIS}/1"
    )
    celery.conf.task_default_queue = "core_to_ai_queue"
    return celery


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def save_url(
    target_url: str,
    internal_id: str = Depends(get_internal_id),
    db: Any = Depends(get_db),
):
    """
    DB에 새로운 URL정보를 적재합니다.

     - :param **target_url**: 적재하고자 하는 URL입니다. og_url 로 대체되어 DB에 저장됩니다.
     - :param **internal_id**: 사용자 내부 아이디 (Header)
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    # Header 크롤링 진행
    try:
        resource = fetch_og_data(target_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL 처리 중 에러가 발생했습니다: {e}")

    if not resource:
        raise HTTPException(status_code=404, detail="해당 사이트를 크롤링할 수 없습니다.")

    # 새 Url 인스턴스 생성
    new_url = Url(
        url=target_url,  # og_url 말고 사용자 url 그대로 삽입
        title=resource["og_title"],
        image=resource["og_image"],
        description=resource["og_description"],
        status=False,  # 기본값 사용
        created_at=datetime.utcnow(),
    )

    urls = user.urls
    urls.append(new_url)
    db.commit()

    return {"message": "생성 완료.", "url_id": new_url.id}


@router.get(path="/", response_model=UrlDto)
async def load_url(
    url_id: str,
    internal_id: str = Depends(get_internal_id),
    db: Any = Depends(get_db),
):
    """
    url_id를 기반으로 해당 URL의 정보를 불러옵니다.

     - :param **url_id**: URL 고유 번호
     - :param **internal_id**: 사용자 내부 아이디 (Header)
     - :return **UrlDto**: URL 정보, status로 분석 완료 여부 확인가능
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    # Url 조회
    url = db.query(Url).filter(Url.id == url_id).first()
    if url is None:
        raise HTTPException(status_code=404, detail="해당하는 id의 url 정보를 찾을 수 없습니다.")

    url_dto = UrlDto(
        url=url.url,
        title=url.title,
        image=url.image,
        description=url.description,
        status=url.status,
    )

    return url_dto


@router.delete(path="/", status_code=status.HTTP_200_OK)
async def delete_url(
    url_id: str,
    internal_id: str = Depends(get_internal_id),
    db: Any = Depends(get_db),
):
    """
    url_id를 기반으로 해당 URL의 정보를 삭제합니다.

     - :param ****: URL 고유 번호
     - :param **internal_id**: 사용자 내부 아이디 (Header)
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    # Url 조회
    url = db.query(Url).filter(Url.id == url_id).first()
    if url is None:
        raise HTTPException(status_code=404, detail="해당하는 id의 url 정보를 찾을 수 없습니다.")

    db.delete(url)
    db.commit()

    return {"message": "삭제 완료."}


@router.put(path="/calculate", status_code=status.HTTP_200_OK)
async def calculate_url(
    url_id: str,
    internal_id: str = Depends(get_internal_id),
    db: Any = Depends(get_db),
    celery: Any = Depends(get_core_worker),
):
    """
    해당하는 URL의 추천 데이터를 생성합니다.
    URL 입력을 받아서 크롤링을 거쳐 raw_text로 변환합니다.
    이후 raw_text -> vector 과정을 AI Server를 통해 진행합니다.
    최종적으로 knn search를 통해 해당 vector와 유사한 관광지를 전달합니다.

     - :param **url_id**: URL 고유 번호
     - :param internal_id: 사용자 내부 아이디 (Header)
     - :return task_id: 해당 task에 대한 id값으로 redis 디버깅용으로 사용됩니다 (프론트 페이지에서 사용 X)
    """
    # Url 조회
    url = db.query(Url).filter(Url.id == url_id).first()
    if url is None:
        raise HTTPException(status_code=404, detail="해당하는 id의 url 정보를 찾을 수 없습니다.")

    # 1. 크롤링 진행
    try:
        # 크롤링 하려는 사이트가 크롤링 가능한지 검증
        if re.match(r"https?://blog.naver.com/PostView.*", url.url):  # 1. 네이버 PC
            raw_text = crawl_naver_blog(url.url)
        elif re.match(r"https?://m.blog.naver.com/.*", url.url):  # 2. 네이버 모바일
            raw_text = crawl_naver_blog(url.url)
        elif re.match(
            r"https?://blog.naver.com/.*", url.url
        ):  # 3. 네이버 PC (inner iframe)
            raw_text = crawl_naver_blog(delete_iframe(url.url))
        # elif re.match(r'https?://.*\.tistory.com/.*', url.url):
        #     crawl_tistory(url.url)
        # elif re.match(r'https?://(www\.)?youtube\.com/.*', url.url) or re.match(r'https?://youtu\.be/.*', url):
        #     crawl_youtube(url.url)
        else:
            raise HTTPException(status_code=400, detail="지원되지 않는 URL 형식입니다.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"URL 처리 중 에러가 발생했습니다: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"크롤링 중 예상치 못한 에러가 발생했습니다: {e}")

    # 2. 임베딩 진행
    # https://docs.celeryq.dev/en/stable/userguide/calling.html
    task = celery.send_task(
        "ai_worker.vector_embedding",
        kwargs={"url_id": url_id, "raw_text": raw_text},
    )
    return {"message": "전달 완료. [core -> ai]", "task_id": task.id}


@router.get("/result/{url_id}")
def get_calculated_result(
    url_id: str,
    db: Any = Depends(get_db),
    es: Any = Depends(get_es_client),
    collection: Any = Depends(get_m_db),
):
    # 모든 갱신 작업은 core_worker에 이관하였으므로, status만 조회하면 됨
    # Url 조회
    url = db.query(Url).filter(Url.id == url_id).first()

    if not url.status:
        raise HTTPException(status_code=400, detail="해당 URL에 대한 추천 벡터가 생성되지 않았습니다.")

    url_vector = url.vector
    url_vector = np.frombuffer(url_vector, dtype=float)
    url_vector = np.nan_to_num(url_vector)

    # Elasticsearch KNN 검색 및 결과 처리
    knn_query = {
        "knn": {
            "field": "text_vector",
            "query_vector": url_vector,
            "k": 11,
            "num_candidates": 100,
        },
        "fields": ["name", "spot_id"],
        "size": 11,
    }

    try:
        knn_response = es.search(index=index_name, body=knn_query)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Elasticsearch 검색 중 예외가 발생했습니다: {e}"
        )

    # 유사한 관광지 저장
    similar_spots = []
    for hit in knn_response["hits"]["hits"][1:]:
        spot_id = hit["_source"]["spot_id"]
        spot = collection.find_one({"spot_id": {"$eq": spot_id}})
        spot = SimpleSpotDto(
            spot_id=spot_id,
            name=spot.get("name", None),
            address=spot.get("address", ""),
            image_url=spot.get("depiction")[0] if spot.get("depiction") else "",
        )
        similar_spots.append(spot)

    if not similar_spots:
        raise HTTPException(status_code=404, detail="유사한 관광지를 찾을 수 없습니다.")

    return similar_spots
