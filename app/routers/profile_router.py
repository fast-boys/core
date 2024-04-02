from io import BytesIO
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

from schemas.profile_dto import UserInfoResponse
from services.gcs import (
    create_secure_path,
    process_profile_image,
    upload_to_gcs,
    upload_to_open_gcs,
)
from services.profile import get_profile_image_signed_url
from services.profile import get_internal_id
from database import get_db
from sqlalchemy.orm import Session

from models.user import User

router = APIRouter(tags=["user_profile"], prefix="/profile")


@router.get("/")
async def get_user_profile(
    internal_id: str = Depends(get_internal_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    user_data = UserInfoResponse(
        username=user.nickname,
        profileImage=None if user.profile_image == "profiles/defaultProfile.svg" else user.profile_image,
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
    profileName: str = Form(...),
    profileImg: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.internal_id == internal_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    check_duplicate = db.query(User).filter(User.nickname == profileName).first()

    if not check_duplicate:
        user.nickname = profileName

    if user == check_duplicate:
        check_duplicate = None

    if profileImg and profileImg.filename:
        image_data = await profileImg.read()
        image_stream = BytesIO(image_data)
        # 이미지 처리
        processed_image = process_profile_image(image_stream)
        destination_blob_name = create_secure_path(user.id, "png")

        # 이미지를 GCP에 업로드하고 사인된 URL을 가져옴
        public_url = upload_to_open_gcs(processed_image, destination_blob_name)

        # userinfo에 공개 URL을 저장
        user.profile_image = public_url

    db.commit()

    return {"data": "duplicate" if check_duplicate else "valid"}
