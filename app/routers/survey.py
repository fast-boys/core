from typing import List, Any
from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import numpy as np
import base64

from schemas.spot_dto import SimpleSpotDto
from services.survey import calculate_user_vector
from services.profile import get_internal_id
from database import get_db, get_m_db, get_es_client
from models.user import User

router = APIRouter(tags=["User Survey"], prefix="/survey")


@router.post(path="/selected")
async def update_user_vector(
    spots: List[str] = Body(...),  # 설문시 선택한 관광지의 spot_id 리스트
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
    es_client: Elasticsearch = Depends(get_es_client),
):
    """
    설문조사를 완료하고, 사용자의 초기 벡터를 업데이트합니다.

    - **spots**: 설문조사에서 선택된 관광지 spot_id의 리스트입니다.
    - **internal_id**: 사용자의 내부 식별자입니다. (DI원칙으로 자동주입)
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    # 초기 유저 벡터 생성
    user_vector = calculate_user_vector(spots, es_client)
    # print(len(user_vector))   # 768
    user_vector = user_vector.tobytes()
    # user_vector = base64.b64encode(user_vector).decode("utf-8")
    user.vector = user_vector  # ORM Update

    db.commit()

    return {"message": "설문 반영 완료."}


@router.get(path="/random_spot", response_model=List[SimpleSpotDto])
async def get_random_spot(
    category: int, count: int = 5, collection: Any = Depends(get_m_db)
):
    """
    특정 카테고리에 해당하는 랜덤 관광지를 반환합니다.

    아래의 입력을 받아 반환합니다.
    - :param **category**: 특정 카테고리 번호
    - :param **count**: 받고자 하는 관광지 갯수 (기본값 5개)
    - :return **List[SimpleSpotDto]**: 관광지 리스트 반환

    참조, category_info ->
      -  "자연 및 야외 활동": 1,
      -  "스포츠 및 레저": 2,
      -  "문화 및 역사": 3,
      -  "쇼핑 및 시장": 4,
      -  "음식 및 식당": 5,
      -  "숙박 및 휴식": 6,
      -  "체험 및 교육": 7,
      -  "공연 및 엔터테인먼트": 8,
      -  "건축물 및 구조물": 9,
      -  "여행 및 관광 서비스": 10,
      -  "기타": 11
    """
    # 카테고리 번호 유효성 검사
    if category < 1 or category > 11:
        raise HTTPException(
            status_code=400, detail=f"category={category} 가 유효한 값이 아닙니다."
        )

    pipeline = [
        {
            "$match": {
                "category": category,  # 카테고리에 맞는 문서를 필터링
                "depiction": {"$exists": True, "$ne": []},
            }
        },
        {"$sample": {"size": count}},  # 5개 랜덤 추출
    ]
    random_docs = list(collection.aggregate(pipeline))
    spots = []

    for doc in random_docs:
        spot = SimpleSpotDto(
            spot_id=doc.get("spot_id"),
            name=doc.get("name"),
            address=doc.get("address", ""),
            image_url=doc.get("depiction")[0],
        )
        spots.append(spot)

    return spots
