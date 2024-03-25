FROM python:3.8

WORKDIR /app

# 현재 디렉토리의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사
COPY requirements.txt ./

# 필요한 Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉토리의 나머지 파일들을 컨테이너의 /app 디렉토리로 복사
COPY . .

ARG VAULT_TOKEN
ENV VAULT_TOKEN=$VAULT_TOKEN


CMD ["python", "app/main.py", "deploy"]
