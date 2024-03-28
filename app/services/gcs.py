import asyncio
from datetime import datetime
import hashlib
from io import BytesIO
import json
import shutil
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from google.cloud import storage
import os
from google.oauth2 import service_account

from vault_client import get_env_value
from PIL import Image

# .env 파일에서 서비스 계정 JSON을 가져옴
service_account_info = json.loads(get_env_value("GCP_SERVICE_ACCOUNT_JSON"))
# 서비스 계정 정보를 사용하여 인증 정보 생성
credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)
# 인증 정보를 사용하여 Storage 클라이언트 생성
storage_client = storage.Client(credentials=credentials)

bucket_name = "fastravel-bucket"
bucket = storage_client.bucket(bucket_name)


async def delete_file_after_delay(filepath, delay=6):
    await asyncio.sleep(delay)  # 지정된 시간(초) 동안 대기
    if os.path.exists(filepath):
        os.remove(filepath)


def upload_to_gcs(file: UploadFile, file_path: str, id: str):
    # 임시 파일 생성
    os.makedirs(f"/home/ubuntu/fastravel_storage", exist_ok=True)
    temp_file = f"/home/ubuntu/fastravel_storage/{id}.{file.filename.split('.')[-1]}"
    with open(temp_file, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # GCS에 업로드
    blob = bucket.blob(file_path)
    blob.upload_from_filename(temp_file)


def process_profile_image(image_file, output_size=(200, 200)):
    with Image.open(image_file) as img:
        # 이미지를 정사각형으로 자르기
        min_dimension = min(img.size)
        center = img.width // 2, img.height // 2
        half_min = min_dimension // 2
        crop_area = (
            center[0] - half_min,
            center[1] - half_min,
            center[0] + half_min,
            center[1] + half_min,
        )
        img_cropped = img.crop(crop_area)

        # 이미지 크기 조정
        img_resized = img_cropped.resize(output_size, Image.Resampling.LANCZOS)

        # 처리된 이미지를 BytesIO 스트림으로 변환
        img_bytes = BytesIO()
        img_resized.save(img_bytes, format="PNG")
        img_bytes.seek(0)  # 스트림의 시작으로 커서를 이동

        return img_bytes


def upload_to_open_gcs(image_data, destination_blob_name):
    blob = bucket.blob(destination_blob_name)

    # 이미지 데이터로부터 바로 업로드
    blob.upload_from_string(image_data.getvalue(), content_type="image/png")
    # Blob을 공개적으로 설정
    blob.make_public()
    # 공개 URL 반환
    return blob.public_url


def create_secure_path(user_id, file_extension):
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # 사용자 ID를 해싱하여 파일 경로에 사용할 고유한 문자열을 생성
    secure_hash = hashlib.sha256(str(user_id).encode()).hexdigest()
    return f"profiles/{secure_hash}/profile_image/profile_{date_str}{file_extension}"


def create_plan_secure_path(user_id, file_extension):
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # 사용자 ID를 해싱하여 파일 경로에 사용할 고유한 문자열을 생성
    secure_hash = hashlib.sha256(str(user_id).encode()).hexdigest()
    return f"plans/{secure_hash}/plans_image/plan_{date_str}{file_extension}"


def generate_signed_url(blob_path: str, expiration: int = 600) -> str:
    """GCS의 서명된 url로 임시 접근 권한 제공"""
    blob = bucket.blob(blob_path)
    # 현재 시간으로부터 expiration(초) 후를 만료 시간으로 설정
    expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=expiration)
    # `expiration`에 `datetime` 객체를 전달
    signed_url = blob.generate_signed_url(expiration=expiration_time)
    return signed_url


def download_from_gcs(source_blob_name, destination_file_name):
    blob = bucket.blob(source_blob_name)
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
    blob.download_to_filename(destination_file_name)


def get_image_stream(file_path: str):
    # Google Cloud Storage에서 이미지 스트리밍
    storage_client = storage.Client()
    bucket = storage_client.bucket("ssafy-bucket")
    blob = bucket.blob(file_path)
    stream = blob.download_as_stream()

    return StreamingResponse(stream, media_type="image/jpeg")
