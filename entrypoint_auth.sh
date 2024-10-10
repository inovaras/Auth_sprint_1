#!/bin/sh
# if [ $PG_DATABASE_TYPE = postgres ]
if [ true ]
then
    echo "Waiting postgres..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 0.1
    done
fi
alembic upgrade head &&\
gunicorn -w 4 -k uvicorn_worker.UvicornH11Worker --bind 0.0.0.0:8080 main:app