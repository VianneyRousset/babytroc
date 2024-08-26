#!/usr/bin/env sh

NAME="kindbaby-${1}"
ID=$(docker ps | grep ${NAME} | cut --delimiter " " --fields 1)

docker exec -it "$ID" bash
