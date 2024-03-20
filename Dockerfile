FROM python:3.8

WORKDIR /app

COPY requirements.txt ./
COPY .idea ./.idea
COPY app ./app
COPY google_service_key.json ./

ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app/main.py", "deploy"]
