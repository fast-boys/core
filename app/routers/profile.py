import uuid
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Request,
    Response,
    UploadFile,
)

from schemas.profile import UserInfoResponse
from services.gcs import upload_to_gcs
from services.profile import get_profile_image_signed_url
from services.profile import get_internal_id
from database import get_db
from sqlalchemy.orm import Session

from models.user import User

router = APIRouter(tags=["user_profile"], prefix="/profile")


@router.get("/")
async def read_users_me(
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found User")
    signed_url = get_profile_image_signed_url(user.profile_image)

    user_data = UserInfoResponse(
        username=user.nickname,
        profileImage=signed_url,
    )
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
    return {"data": "duplicate" if user else "valid"}


@router.put("/")
async def update_user_profile(
    background_tasks: BackgroundTasks,
    internal_id: str = Depends(get_internal_id),
    name: str = Form(...),
    profile_img: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    check_duplicate = db.query(User).filter(User.nickname == name).first()

    if not check_duplicate:
        user.nickname = name

    if user == check_duplicate:
        check_duplicate = None

    if profile_img and profile_img.filename:
        img_uuid = str(uuid.uuid4())
        file_path = f"profiles/{img_uuid}"
        user.profile_image = file_path
        background_tasks.add_task(upload_to_gcs, profile_img, file_path)

    db.commit()

    return {"data": "duplicate" if check_duplicate else "valid"}
