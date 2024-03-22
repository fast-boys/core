import asyncio
import json
import shutil
from dotenv import load_dotenv
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from google.cloud import storage
import os
from google.oauth2 import service_account
import httpx

# .env 파일에서 환경 변수 로드
load_dotenv()

# .env 파일에서 서비스 계정 JSON을 가져옴
service_account_info = json.loads(os.getenv("GCP_SERVICE_ACCOUNT_JSON"))
# 서비스 계정 정보를 사용하여 인증 정보 생성
credentials = service_account.Credentials.from_service_account_info(service_account_info)
# 인증 정보를 사용하여 Storage 클라이언트 생성
storage_client = storage.Client(credentials=credentials)


async def delete_file_after_delay(filepath, delay=6):
    await asyncio.sleep(delay)  # 지정된 시간(초) 동안 대기
    if os.path.exists(filepath):
        os.remove(filepath)


def upload_to_gcs(file: UploadFile, file_path: str, id: str):
    bucket_name = "fastravel-bucket"
    bucket = storage_client.bucket(bucket_name)

    # 임시 파일 생성
    os.makedirs(f"/home/ubuntu/fastravel_storage", exist_ok=True)
    temp_file = f"/home/ubuntu/fastravel_storage/{id}.{file.filename.split('.')[-1]}"
    with open(temp_file, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # GCS에 업로드
    blob = bucket.blob(file_path)
    blob.upload_from_filename(temp_file)

    # 임시 파일 삭제
    # os.remove(temp_file)


def save_to_local_directory(file: UploadFile, file_name: str, id: str):
    # 도커 컨테이너 내 저장할 경로 지정 (볼륨 마운트 경로)
    base_path = "/app/storage"

    # 파일 저장 경로 생성
    save_path = os.path.join(base_path, f"{id}.{file_name}")

    # 디렉토리가 존재하지 않는 경우 생성
    os.makedirs(base_path, exist_ok=True)

    # 파일 저장
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    print(f"File saved to {save_path}")


def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    bucket_name = "fastravel-bucket"
    bucket = storage_client.bucket(bucket_name)
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
