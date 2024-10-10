FROM python:3.11-slim

WORKDIR /auth_service/src

COPY requirements.txt .

RUN  apt-get update && \
    apt-get install -y htop netcat-traditional gcc &&\
    apt-get clean

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn uvicorn-worker

COPY configs /configs
COPY ./auth_service/src .
COPY ./auth_service/tests /auth_service/tests

EXPOSE 8080

COPY . .

RUN chmod 777 ./entrypoint_auth.sh

ENTRYPOINT ./entrypoint_auth.sh
