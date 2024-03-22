import base64
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Path, Request, Response, UploadFile

from services.profile import download_from_gcs, upload_to_gcs
from services.utils import get_internal_id
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
    download_from_gcs

    user_data = {
        "username": user.nickname,
        "profileImage": user.profile_picture_url,
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
    print("??")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    print(profile_img.filename)
    content = profile_img.file.read()
    if profile_img and profile_img.filename:
        """파일 저장 또는 처리
        file_location = f"C:/files/{profile_img.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(profile_img.file.read())
        """
        file_path = f"profiles/{user.internal_id}"
        background_tasks.add_task(upload_to_gcs, profile_img, file_path)
        upload_to_gcs(profile_img, file_path, user.internal_id)
        file_name = profile_img.filename.split(".")[-1]
        user.profile_image = f"/app/storage/{user.internal_id}.{profile_img.filename.split('.')[-1]}"

    user.name = name
    # user.profile_image = f"C:/files/{user.internal_id}.{profile_img.filename.split('.')[-1]}"
    db.commit()
    file_base64 = base64.b64encode(content).decode("utf-8")

    user_data = {
        "name": name,
        "profile_image": file_base64,
    }
    return user_data
