import asyncio
import datetime
import json
import shutil
from dotenv import load_dotenv
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from google.cloud import storage
import os
from google.oauth2 import service_account

# .env 파일에서 환경 변수 로드
load_dotenv()

# .env 파일에서 서비스 계정 JSON을 가져옴
service_account_info = json.loads(os.getenv("GCP_SERVICE_ACCOUNT_JSON"))
# 서비스 계정 정보를 사용하여 인증 정보 생성
credentials = service_account.Credentials.from_service_account_info(service_account_info)
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
