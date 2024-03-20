from multiprocessing import Process
import sys
from fastapi import FastAPI
import uvicorn

from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["https://localhost", "https://localhost:3000", "추가하십시오."]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.add_middleware(
#     SessionMiddleware,
#     secret_key=os.getenv("SESSION_SECRET_KEY"),
#     https_only=True,
#     same_site="None",
# )


"""
# 서비스시에 없애야 할 듯. 자동 마이그레이션.
@app.on_event("startup")
async def startup_event():
    # Alembic 설정 객체 생성
    alembic_cfg = Config("alembic.ini")  # 'alembic.ini' 파일의 경로를 정확히 지정하세요.
    # 마이그레이션 업그레이드 명령 실행
    command.upgrade(alembic_cfg, "head")
"""


def local_run():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
        ssl_keyfile="../../localhost-key.pem",
        ssl_certfile="../../localhost.pem",
        forwarded_allow_ips="*",  # 모든 프록시된 IP 주소 허용
        proxy_headers=True,  # X-Forwarded-Proto 헤더를 신뢰
    )


def deploy_run():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        forwarded_allow_ips="*",  # 모든 프록시된 IP 주소 허용
        proxy_headers=True,  # X-Forwarded-Proto 헤더를 신뢰
        root_path="/api",
    )


# 추가적인 인증 및 사용자 관리 로직
if __name__ == "__main__":
    if sys.argv[1] == "local":
        api_process = Process(target=local_run)
        api_process.start()
        api_process.join()
    elif sys.argv[1] == "deploy":
        api_process = Process(target=deploy_run)
        api_process.start()
        api_process.join()
