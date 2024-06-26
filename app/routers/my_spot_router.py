from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pymongo import MongoClient

from schemas.spot_dto import MyMemoResponseDto, MySpotRequestDto, MySpotResponseDto
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
        spot_info = collection.find_one({"spot_id": {"$eq": str(my_spot.spot_id)}})
        if spot_info is None:
            continue  # 관광지 정보가 없는 항목은 건너뜀
        if my_spot.like_status is False:
            continue  # 좋아요를 누르지 않은 항목은 건너뜀
        properties = spot_info.get("properties", {})
        # 이미지, 타이틀, 주소, 메모 필요
        res = MySpotResponseDto(
            spot_id=str(my_spot.spot_id),
            name=spot_info.get("name"),
            address=properties.get("address", ""),
            image_url=spot_info.get("depiction")[0] if spot_info.get("depiction") else "",
            memo=my_spot.memo,
            created_at=my_spot.created_date,
        )
        response.append(res)

    return response


@router.post("/")
async def create_my_spot(
    request: MySpotRequestDto,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
    collection: MongoClient = Depends(get_m_db),
):
    """
    사용자가 좋아요를 한 관광지 (My Spot)을 추가합니다.

    :param **MySpotRequestDto**: 관광지 식별자 및 메모 정보
    :param **internal_id**: 사용자 아이디 헤더
    """
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    if not collection.find_one({"spot_id": {"$eq": str(request.spot_id)}}):
        raise HTTPException(status_code=404, detail="해당하는 관광지를 찾을 수 없습니다.")

    # 이미 있으면 추가 안함
    existing_spot = db.query(MySpot).filter(MySpot.spot_id == request.spot_id, MySpot.user_id == user.id).first()
    if existing_spot:
        existing_spot.like_status = True
        existing_spot.memo = request.memo
        db.commit()
        return {"message": "좋아요 완료", "spot_id": existing_spot.spot_id}

    # if existing_spot and existing_spot.like_status is True:
    #     return {"message": "이미 추가된 관광지 입니다.", "spot_id": existing_spot.spot_id}

    my_spots = user.my_spots
    new_spot = MySpot(
        user_id=user.id,
        spot_id=request.spot_id,
        memo=request.memo,
        like_status=True,
    )

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
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    my_spot = db.query(MySpot).filter(MySpot.spot_id == spot_id, MySpot.user_id == user.id).first()
    if my_spot is None:
        raise HTTPException(status_code=404, detail="해당하는 id의 my_spot 정보를 찾을 수 없습니다.")

    my_spot.like_status = False
    if my_spot.like_status is False and (my_spot.memo is None or my_spot.memo == ""):
        db.delete(my_spot)
    db.commit()

    return {"message": "삭제 완료."}


@router.put("/memo")
async def edit_memo(
    spot_id: str,
    memo: str,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    """
    사용자가 좋아요를 한 관광지 (My Spot)의 메모를 수정합니다.

    :param **spot_id**: 관광지 식별자
    :param **memo**: 수정할 메모
    :param **internal_id**: 사용자 내부 아이디 (Header)
    """
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    my_spot = db.query(MySpot).filter(MySpot.spot_id == spot_id, MySpot.user_id == user.id).first()
    if my_spot is None:
        my_spot = MySpot(
            user_id=user.id,
            spot_id=spot_id,
            created_date=datetime.utcnow().date(),
            like_status=False,
        )
        db.add(my_spot)
    my_spot.memo = memo
    db.commit()

    return {"message": "수정 완료."}


@router.get("/memo")
async def get_memo_list(
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
) -> List[MyMemoResponseDto]:
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    my_spots = db.query(MySpot).filter(MySpot.user_id == user.id, MySpot.memo.isnot(None), MySpot.memo.isnot("")).all()
    memo_list = [MyMemoResponseDto.from_orm(my_spot) for my_spot in my_spots]
    return memo_list


@router.delete("/memo/{spot_id}")
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
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당하는 유저를 찾을 수 없습니다.")

    my_spot = db.query(MySpot).filter(MySpot.spot_id == spot_id, MySpot.user_id == user.id).first()
    if my_spot is None:
        raise HTTPException(status_code=404, detail="해당하는 id의 my_spot 정보를 찾을 수 없습니다.")

    my_spot.memo = None
    if my_spot.like_status is False and (my_spot.memo is None):
        db.delete(my_spot)
    db.commit()

    return {"message": "삭제 완료."}
