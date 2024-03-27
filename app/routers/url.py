from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List

from services.url import fetch_og_data
from services.profile import get_internal_id
from database import get_db
from models.url import Url
from models.user import User
from schemas.url_dto import UrlDto
from starlette import status

router = APIRouter(tags=["User Url"], prefix="/url")


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def save_url(
    target_url: str,
    internal_id: str = Depends(get_internal_id),
    db: Any = Depends(get_db),
):
    """
    DB에 새로운 URL 정보를 적재합니다.

    :param target_url: 적재하고자 하는 URL입니다. og_url 로 대체되어 DB에 저장됩니다.
    :param internal_id: 사용자 내부 아이디 (Header)
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
    url_id를 기반으로 해당 id의 og 정보를 불러옵니다.

    :param url_id: URL 고유 번호
    :param internal_id: 사용자 내부 아이디 (Header)
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
    url_id를 기반으로 해당 id의 URL 정보를 삭제합니다.

    :param url_id: URL 고유 번호
    :param internal_id: 사용자 내부 아이디 (Header)
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
