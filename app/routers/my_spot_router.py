from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pymongo import MongoClient

from schemas.spot_dto import MySpotRequestDto, MySpotResponseDto
from models.user import User
from models.my_spot import MySpot
from database import get_db, get_m_db


from services.profile import get_internal_id

router = APIRouter(tags=["My spot"], prefix="/my_spot")


@router.get("/list")
async def get_my_spot_list(
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
    collection: MongoClient = Depends(get_m_db),
) -> List[MySpotResponseDto]:
    """
    사용자가 좋아요를 한 관광지 (My Spot)을 조회합니다.

    :param **internal_id**: 사용자 아이디 헤더
    :return **List[MySpotDto]**: 클라이언트에 전달하는 내 관광지 정보:
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    response = []

    my_spots = user.my_spots
    for my_spot in my_spots:
        spot_info = spot = collection.find_one({"spot_id": {"$eq": my_spot.id}})
        # 이미지, 타이틀, 주소, 메모 필요
        res = MySpotResponseDto(
            spot_id=my_spot.id,
            name=spot_info.get("name"),
            address=spot_info.get("address"),
            image_url=spot_info.get("image_url"),
            memo=my_spot.memo,
            created_at=my_spot.created_date,
        )
        response.append(res)

    return response


@router.post("/{spot_id}")
async def create_my_spot(
    request: MySpotRequestDto,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    """
    사용자가 좋아요를 한 관광지 (My Spot)을 추가합니다.

    :param **MySpotRequestDto**: 관광지 식별자 및 메모 정보
    :param **internal_id**: 사용자 아이디 헤더
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    my_spots = user.my_spots
    new_spot = MySpot(
        id=user.id,
        spot_id=request.spot_id,
        memo=request.memo,
        created_date=datetime.utcnow().date(),
    )

    # 이미 있으면 추가 필요
    my_spots.append(new_spot)
    db.commit()
    return {"message": "추가 완료.", "spot_id": new_spot.spot_id}


@router.delete("/{spot_id}")
async def delete_my_spot(
    spot_id: str,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    """
    사용자가 좋아요를 한 관광지 (My Spot)을 삭제합니다.

     - :param **spot_id**: 관광지 식별자
     - :param **internal_id**: 사용자 내부 아이디 (Header)
    """
    # User Info 조회
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    # My Spots 조회
    my_spot = db.query(MySpot).filter(MySpot.spot_id == spot_id, MySpot.id == user.id).first()
    if my_spot is None:
        raise HTTPException(status_code=404, detail="해당하는 id의 my_spot 정보를 찾을 수 없습니다.")

    db.delete(my_spot)
    db.commit()

    return {"message": "삭제 완료."}
