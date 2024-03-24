from celery import Celery
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# 환경 변수에서 RabbitMQ 연결 정보 가져오기
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')

# Celery 애플리케이션 생성
celery_app = Celery(
    __name__,
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//',
    backend='rpc://',
    include=['tasks']
)
