#!/bin/sh

sed -i "s|FS_HOST=host.docker.internal|FS_HOST=${FS_HOST:-host.docker.internal}|" .env
sed -i "s|FS_ESL_PORT=8021|FS_ESL_PORT=${FS_ESL_PORT:-8021}|" .env
sed -i "s|FS_ESL_PASSWORD=ClueCon|FS_ESL_PASSWORD=${FS_ESL_PASSWORD:-ClueCon}|" .env
sed -i "s|LOG_LEVEL=info|LOG_LEVEL=${LOG_LEVEL:-info}|" .env
sed -i "s|LOG_TO_FILE=false|LOG_TO_FILE=${LOG_TO_FILE:-false}|" .env
sed -i "s|LOG_FILE=fs_esl.log|LOG_FILE=${LOG_FILE:-fs_esl.log}|" .env
sed -i "s|SIP_ENDPOINT=extension@domain.com|SIP_ENDPOINT=${SIP_ENDPOINT:-extension@domain.com}|" .env
sed -i "s|EXTENSION_TO_CALL=1000|EXTENSION_TO_CALL=${EXTENSION_TO_CALL:-1000}|" .env

python app.py