import base64
import os
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from fastapi.security import HTTPBearer

from services.utils import get_internal_id
from database import get_db
from sqlalchemy.orm import Session

from models.user import User

router = APIRouter(tags=["user_profile"], prefix="/profile")


@router.get("/")
async def read_users_me(
    request: Request,
    response: Response,
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found User")

    user_data = {
        "nickname": user.nickname,
    }
    return user_data


@router.get("/{nickname}/duplicate")
async def check_nickname_duplicate(
    nickname: str = Path(..., description="The nickname to check for existence"),
    db: Session = Depends(get_db),
):
    """
    닉네임 중복 체크

    ### Args:
    - nickname (str): 검사하기 위한 닉네임 (입력값)

    ### Returns:
    - {"duplicate": True/False}
    """
    user = db.query(User).filter(User.nickname == nickname).first()
    return {"duplicate": True if user else False}
