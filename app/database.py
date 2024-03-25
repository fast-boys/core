# database.py
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()  # 환경 변수 로드
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    # 커넥션 풀 설정
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# declarative base 클래스를 생성합니다
Base = declarative_base()

# 세션 팩토리를 생성합니다
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB 데이터베이스 URL
MONGODB_URL = os.getenv("MONGODB_URL")

# MongoDB 클라이언트 생성
mongo_client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)  # 5초 타임아웃
"""
mongo_client = MongoClient(
    "mongodb://localhost:27017/",
    maxPoolSize=50,
    connectTimeoutMS=30000,
    serverSelectionTimeoutMS=30000,
)
"""
m_db = mongo_client["S10P22D204"]
m_collection = m_db["tripdata"]

ES_URL = os.getenv("ES_URL")
ES_CERT_FINGERPRINT = os.getenv("ES_CERT_FINGERPRINT")
ES_PASSWORD = os.getenv("ES_PASSWORD")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_m_db():
    try:
        yield m_collection
    finally:
        pass


def init_es_client():
    return Elasticsearch(
        hosts=[ES_URL],
        ssl_assert_fingerprint=ES_CERT_FINGERPRINT,
        basic_auth=("elastic", ES_PASSWORD),
        request_timeout=30,
    )


def get_es_client():
    es_client = init_es_client()
    try:
        yield es_client
    finally:
        es_client.close()
