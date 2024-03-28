from multiprocessing import Process

from fastapi.responses import JSONResponse
from vault_client import get_env_value
from routers import profile, place, recommend, travel, survey, url, debug
import sys
from fastapi import FastAPI, Request
import uvicorn
from models import user, plan, user_plan, visit_place, spot, city, article, my_spot
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "https://localhost",
    "https://localhost:3000",
    "https://localhost:8000",
    "https://j10d204.p.ssafy.io",
    "http://j10d204.p.ssafy.io",
    "http://localhost:3000",
    "http://192.168.100.166",
    "http://localhost:5173",
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gateway로부터 들어오는지 확인하는 로직
@app.middleware("http")
async def check_header_middleware(request: Request, call_next):
    # 예외 경로 처리 -> swagger, openapi.json
    # path_whitelist = ["/docs", "/openapi.json"]
    # if request.url.path in path_whitelist:
    #     return await call_next(request)

    # secret_key 헤더가 없거나 틀리면 401 반환
    # secret_key = request.headers.get("SECRET_KEY_HEADER")
    # if secret_key != "fastand6":
    #     return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    response = await call_next(request)
    return response


# 테스트용
@app.get("/echo")
def echo():
    return {"data": "안녕하세요"}


# session middleware (client side session)
"""
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    https_only=True,
    same_site="None",
)
"""


app.include_router(profile.router)
app.include_router(place.router)
app.include_router(recommend.router)
app.include_router(travel.router)
app.include_router(survey.router)
app.include_router(url.router)
app.include_router(debug.router)

# app 실행 시 마이그레이션 자동 실행 코드
"""
@app.on_event("startup")
async def startup_event():
    # Alembic 설정 객체 생성
    alembic_cfg = Config("alembic.ini")  # 'alembic.ini' 파일의 경로를 정확히 지정
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
        # ssl_keyfile="../../localhost-key.pem",
        # ssl_certfile="../../localhost.pem",
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
        # root_path="/api",
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
