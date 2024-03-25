FROM python:3.8

WORKDIR /app

# 현재 디렉토리의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사
COPY requirements.txt ./

# 필요한 Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉토리의 나머지 파일들을 컨테이너의 /app 디렉토리로 복사
COPY . .

ARG DATABASE_URL
ARG MONGODB_URL
ARG GCP_SERVICE_ACCOUNT_JSON
ARG ES_URL
ARG ES_PASSWORD
ARG ES_CERT_FINGERPRINT
ARG ES_IDX_NAME

ENV DATABASE_URL=$DATABASE_URL
ENV MONGODB_URL=$MONGODB_URL
ENV GCP_SERVICE_ACCOUNT_JSON=$GCP_SERVICE_ACCOUNT_JSON
ENV ES_URL=$ES_URL
ENV ES_PASSWORD=$ES_PASSWORD
ENV ES_CERT_FINGERPRINT=$ES_CERT_FINGERPRINT
ENV ES_IDX_NAME=$ES_IDX_NAME

CMD ["python", "app/main.py", "deploy"]
