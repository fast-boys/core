FROM python:3.8

WORKDIR /app

# 현재 디렉토리의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사
COPY requirements.txt ./

# 필요한 Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# supervisord 설치
RUN pip install supervisor

# 현재 디렉토리의 나머지 파일들을 컨테이너의 /app 디렉토리로 복사
COPY . .

ARG VAULT_TOKEN
ENV VAULT_TOKEN=$VAULT_TOKEN

# log 기록용 폴더
RUN mkdir -p /etc/log

# supervisord.conf 파일을 컨테이너에 복사합니다.
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD를 supervisord로 변경하여 여러 프로세스를 함께 실행합니다.
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
